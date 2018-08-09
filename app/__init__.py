from flask import Flask, request, jsonify, abort
import pymongo
from pymongo import MongoClient

from . import utils

__version__ = "0.4.0"

app = Flask(__name__)

client = MongoClient()

db = client["dtool_info"]
collection = db["datasets"]

app.config["mongo_client"] = client
app.config["mongo_db"] = db
app.config["mongo_collection"] = collection

# Index entire document.
collection.create_index([("$**", pymongo.TEXT)])


@app.route("/")
def index():
    message = "{} registered datasets".format(
        app.config["mongo_collection"].count()
    )
    return message


@app.route("/lookup_datasets/<uuid>")
def lookup_datasets(uuid):
    datasets = utils.lookup_datasets(
        app.config["mongo_collection"],
        uuid
    )
    return jsonify(datasets)


@app.route("/register_dataset", methods=["POST"])
def register_dataset():
    dataset_info = request.get_json()
    uuid = utils.register_dataset(
        app.config["mongo_collection"],
        dataset_info
    )
    if uuid is None:
        abort(400)
    return uuid


@app.route("/search_for_datasets", methods=["POST"])
def search_for_datasets():
    query = request.get_json()
    print(query)
    datasets = utils.search_for_datasets(
        app.config["mongo_collection"],
        query
    )
    print("datasets in route {}".format(datasets))
    return jsonify(datasets)
