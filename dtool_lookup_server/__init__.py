import sys

from abc import ABC, abstractmethod
from pkg_resources import iter_entry_points

from flask import Flask, request
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


class PluginABC(ABC):
    """Common base class for all plugins.

    There are different groups of plugins, i.e. search plugin, retrieve plugin,
    and extension plugins. These groups differ on where within this lookup
    server core they are hooked to. All of them are discovered via the
    python entrypoints mechanism.
    """
    @abstractmethod
    def register_dataset(self, dataset_info):
        """Register a dataset.

        The base URI is in the dataset_info. It is assumed that preflight checks
        have been made to ensure that the base URI has been registered and that
        the user has permissions to perform the action.
        """
        pass

    @abstractmethod
    def get_config(self):
        """Return the Config object of the retrieve plugin."""
        pass


class SearchABC(PluginABC):
    """Any search plugin must inherit from this base class."""

    @abstractmethod
    def search(self, query):
        """Search for datasets.

        It is assumed that preflight checks have been made to ensure that the
        user has permissions to perform the action and that the base URIs in the
        query have been limited to those the user has permissions to search.

        The search method is hooked into utils.search_datasets_by_user and
        MUST process a query argument adhering to SearchDatasetSchema,
        meaning

            {
              "base_uris": [
                "string"
              ],
              "free_text": "string",
              "uuids": [
                "string"
              ],
              "creator_usernames": [
                "string"
              ],
              "tags": [
                "string"
              ]
            }

        at the time of writing.

        The search plugin SHOULD make use of "OR" logic for the items in
        "base_uris" and "creator_usernames" lists, but use "AND" logic for
        filtering the search based on the items in the tags list.
        """
        pass

    @abstractmethod
    def lookup_uris(self, uuid, base_uris):
        """Return list of URIs for a dataset defined by a UUID.

        It is assumed that preflight checks will be performed to provide
        a list of base URIs that the user is allowed to search through.
        """
        pass


class RetrieveABC(ABC):
    """Any retrieve plugin must inherit from this base class."""

    @abstractmethod
    def get_readme(self, uri):
        """Return the dataset readme.

        It is assumed that preflight checks have been made to ensure that the
        user has permissions to access the URI.
        """
        pass

    @abstractmethod
    def get_manifest(self, uri):
        """Return the dataset manifest.

        It is assumed that preflight checks have been made to ensure that the
        user has permissions to access the URI.
        """
        pass

    @abstractmethod
    def get_annotations(self, uri):
        """Return the dataset annotations.

        It is assumed that preflight checks have been made to ensure that the
        user has permissions to access the URI.
        """
        pass


class ExtensionABC(ABC):
    """Any extension plugin must inherit from this base class.

    An extension MUST implement:
      - a register_dataset(self, dataset_info) method.
      - a get_config() method.
      - a get_blueprint() method. This also means the extension MUST provide a
        single blueprint.

    An extension MAY implement
      - an init_app(self, app, *args, **kwargs):

    An extension SHOULD:
      - retrieve config parameters in a Flask-typical fashion, i.e.
        from the environment or from file as done within the core at
        dtool_lookup_server.config.Config
      - provide these parameters via the get_config method.
      - access at runtime via global Flask config, i.e. app.config

    The app factory will inject extension config parameters into global
    Flask app config.
    """

    @abstractmethod
    def get_blueprint(self):
        """Return the Flask blueprint to be used for the extension."""

    def init_app(self, app, *args, **kwargs):
        """Called by Flask app factory."""
        pass


sql_db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()


# Load the search plugin.
search_entrypoints = []
for entrypoint in iter_entry_points("dtool_lookup_server.search"):
    print(entrypoint)
    search_entrypoints.append(entrypoint.load())
if len(search_entrypoints) < 1:
    raise(RuntimeError("Please install a search plugin"))
elif len(search_entrypoints) > 1:
    raise(RuntimeError("Too many search plugins; there can be only one"))
search = search_entrypoints[0]()

# Load the retrieve plugin.
retrieve_entrypoints = []
for entrypoint in iter_entry_points("dtool_lookup_server.retrieve"):
    print(entrypoint)
    retrieve_entrypoints.append(entrypoint.load())
if len(retrieve_entrypoints) < 1:
    raise(RuntimeError("Please install a retrieve plugin"))
elif len(retrieve_entrypoints) > 1:
    raise(RuntimeError("Too many retrieve plugins; there can be only one"))
retrieve = retrieve_entrypoints[0]()

# Load any extension plugins.
extensions = []
for entrypoint in iter_entry_points("dtool_lookup_server.extension"):
    print(entrypoint)
    ep = entrypoint.load()
    extensions.append(ep())


plugins = [search, retrieve, *extensions]


def create_app(test_config=None):
    app = Flask(__name__)

    CORS(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(Config)

        # any plugin may provide its own config
        for plugin in plugins:
            # if applicable, plugin config is mapped into global flask config
            app.config.from_object(plugin.get_config())

    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    for plugin in plugins:
        plugin.init_app(app)

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

    # Load dtool-lookup-server extension plugin blueprints.
    for ex in extensions:
        bp = ex.get_blueprint()
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
