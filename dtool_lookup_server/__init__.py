from flask import Flask

from config import Config

__version__ = "0.4.0"

app = Flask(__name__)
app.config.from_object(Config)

from dtool_lookup_server import routes

from dtool_lookup_server import nosql_db
nosql_db.init_mongo_db(app)
