from flask import Flask
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config
from dtool_lookup_server import nosql_db

__version__ = "0.4.0"

mongo = PyMongo()
sql_db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    mongo.init_app(app)

    sql_db.init_app(app)
    migrate = Migrate(app, sql_db)

    from dtool_lookup_server import routes
    app.register_blueprint(routes.bp)

    return app
