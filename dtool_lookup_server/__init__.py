import sys

from abc import ABC, abstractmethod
from pkg_resources import iter_entry_points

from flask import Flask, request
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_smorest import (
    Api,
    Blueprint
)
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

import pymongo

from dtool_lookup_server.config import Config

__version__ = "0.17.2"

MONGO_COLLECTION = "datasets"


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


class SearchABC(ABC):

    @abstractmethod
    def register_dataset(self, dataset_info):
        """Register a dataset.

        The base URI is in the dataset_info. It is assumed that preflight checks
        have been made to ensure that the base URI has been registered and that
        the user has permissions to perform the action.
        """
        pass

    @abstractmethod
    def search(self, query):
        """Search for datasets.

        It is assumed that preflight checks have been made to ensure that the
        user has permissions to perform the action and that the base URIs in the
        query have been limited to those the user has permissions to search.
        """
        pass

    @abstractmethod
    def lookup_uris(self, uuid, base_uris):
        """Return list of URIs for a dataset defined by a UUID.

        It is assumed that preflight checks will be performed to provide
        a list of base URIs that the user is allowed to search through.
        """



sql_db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
mongo = PyMongo()


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
    ma.init_app(app)
    jwt.init_app(app)

    api = Api(app)

    from dtool_lookup_server import (
        config_routes,
        dataset_routes,
        user_routes,
        base_uri_routes,
        user_admin_routes,
        permission_routes,
    )

    api.register_blueprint(config_routes.bp)
    api.register_blueprint(dataset_routes.bp)
    api.register_blueprint(user_routes.bp)
    api.register_blueprint(base_uri_routes.bp)
    api.register_blueprint(user_admin_routes.bp)
    api.register_blueprint(permission_routes.bp)

    # Load dtool-lookup-server plugin blueprints.
    for entrypoint in iter_entry_points("dtool_lookup_server.blueprints"):
        bp = entrypoint.load()
        if not isinstance(bp, Blueprint):
            print(
                "Please use flask_smorest.blueprint.Blueprint instead of flask.Blueprint",  # NOQA
                file=sys.stderr,
            )
            sys.exit(1)
        api.register_blueprint(bp)

    @app.before_request
    def log_request():
        """Log the request header in debug mode."""
        app.logger.debug("Request Headers {}".format(request.headers))
        return None

    return app
