from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config
from dtool_lookup_server import nosql_db

__version__ = "0.4.0"

app = Flask(__name__)
app.config.from_object(Config)

nosql_db.init_mongo_db(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from dtool_lookup_server import routes
