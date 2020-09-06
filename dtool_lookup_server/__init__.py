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

MONGO_COLLECTION = "datasets"
MONGO_DEPENDENCY_VIEW = 'dependencies'


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
    mongo.db[MONGO_COLLECTION].create_index([("$**", pymongo.TEXT)])

    # enable undirected view on dependency graph
    if Config.ENABLE_DEPENDENCY_VIEW:
        aggregation_pipeline = build_undirected_adjecency_lists()
        app.logger.debug("Configured view with {}".format(aggregation_pipeline))
        mongo.db.command(
            'create',
            MONGO_DEPENDENCY_VIEW, viewOn=MONGO_COLLECTION,
            pipeline=aggregation_pipeline)

    sql_db.init_app(app)
    Migrate(app, sql_db)

    jwt.init_app(app)

    from dtool_lookup_server import (
        dataset_routes,
        user_routes,
        base_uri_routes,
        user_admin_routes,
        permission_routes,
    )
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
