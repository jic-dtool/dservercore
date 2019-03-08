from flask import Flask
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config
from dtool_lookup_server import nosql_db

__version__ = "0.4.0"

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
#nosql_db.init_mongo_db(app)

sql_db = SQLAlchemy(app)
migrate = Migrate(app, sql_db)



from dtool_lookup_server import routes, sql_models
