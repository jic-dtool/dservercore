from flask import Flask
import pymongo
from pymongo import MongoClient

__version__ = "0.4.0"

app = Flask(__name__)

from app import routes

client = MongoClient()

db = client["dtool_info"]
collection = db["datasets"]

app.config["mongo_client"] = client
app.config["mongo_db"] = db
app.config["mongo_collection"] = collection

# Index entire document.
collection.create_index([("$**", pymongo.TEXT)])


