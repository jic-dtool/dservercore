from flask import Flask
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

import pymongo

from dtool_lookup_server.config import Config

__version__ = "0.9.0"

MONGO_COLLECTION = "datasets"


class ValidationError(ValueError):
    pass


class AuthenticationError(ValueError):
    pass


class AuthorizationError(ValueError):
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

    return app
