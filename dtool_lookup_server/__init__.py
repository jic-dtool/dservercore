from flask import Flask
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config
from dtool_lookup_server import nosql_db

__version__ = "0.4.0"

mongo = PyMongo()
sql_db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)

    sql_db.init_app(app)
    migrate = Migrate(app, sql_db)

    from dtool_lookup_server import routes
    app.register_blueprint(routes.bp)

    return app
