from flask import Flask, request, jsonify, abort
from pymongo import MongoClient

import utils

app = Flask(__name__)

client = MongoClient()

db = client["dtool_info"]
collection = db["datasets"]

app.config["mongo_client"] = client
app.config["mongo_db"] = db
app.config["mongo_collection"] = collection


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
