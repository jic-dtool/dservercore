import pymongo
from pymongo import MongoClient


def init_mongo_db(app):
    client = MongoClient()
    db = client["dtool_info"]
    collection = db["datasets"]

    app.config["mongo_client"] = client
    app.config["mongo_db"] = db
    app.config["mongo_collection"] = collection

    # Index entire document.
    collection.create_index([("$**", pymongo.TEXT)])
