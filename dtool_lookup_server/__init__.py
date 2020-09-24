from flask import Flask, request
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

import pymongo

from dtool_lookup_server.config import Config
from dtool_lookup_server.graph import build_undirected_adjecency_lists

__version__ = "0.14.1"


class ValidationError(ValueError):
    pass


class AuthenticationError(ValueError):
    pass


class AuthorizationError(ValueError):
    pass


class UnknownBaseURIError(KeyError):
    pass


class UnknownURIError(KeyError):
    pass


mongo = PyMongo()
sql_db = SQLAlchemy()
jwt = JWTManager()


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    mongo.init_app(app)

    # Enable full text searching.
    mongo.db[Config.MONGO_COLLECTION].create_index([("$**", pymongo.TEXT)])

    # enable undirected view on dependency graph
    if Config.ENABLE_DEPENDENCY_VIEW:
        if Config.MONGO_DEPENDENCY_VIEW in mongo.db.list_collection_names():
            if Config.FORCE_REBUILD_DEPENDENCY_VIEW:
                app.logger.warning("Dropping exisitng view '{}'.".format(Config.MONGO_DEPENDENCY_VIEW))
                mongo.db[Config.MONGO_DEPENDENCY_VIEW].drop()

        if Config.MONGO_DEPENDENCY_VIEW not in mongo.db.list_collection_names():
            aggregation_pipeline = build_undirected_adjecency_lists()
            app.logger.debug("Configured view with {}".format(aggregation_pipeline))
            try:
                mongo.db.command(
                    'create',
                    Config.MONGO_DEPENDENCY_VIEW, viewOn=Config.MONGO_COLLECTION,
                    pipeline=aggregation_pipeline)
            except pymongo.errors.OperationFailure as exc:
                app.logger.exception(exc)
                app.logger.warning("Dependency view creation failed. Ignored.")
        else:
            app.logger.info("Existing view '{}' not touched.".format(Config.MONGO_DEPENDENCY_VIEW))

    sql_db.init_app(app)
    Migrate(app, sql_db)

    jwt.init_app(app)

    from dtool_lookup_server import (
        config_routes,
        dataset_routes,
        user_routes,
        base_uri_routes,
        user_admin_routes,
        permission_routes,
    )
    app.register_blueprint(config_routes.bp)
    app.register_blueprint(dataset_routes.bp)
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(base_uri_routes.bp)
    app.register_blueprint(user_admin_routes.bp)
    app.register_blueprint(permission_routes.bp)

    @app.before_request
    def log_request():
        """Log the request header in debug mode."""
        app.logger.debug("Request Headers {}".format(request.headers))
        return None

    return app
