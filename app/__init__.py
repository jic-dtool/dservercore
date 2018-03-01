from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
from bson.objectid import ObjectId

from utils import dataset_info_is_valid

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


@app.route("/lookup_dataset_info/<uuid>")
def lookup_dataset_info(uuid):
    dataset_info = app.config["mongo_collection"].find_one()
    del dataset_info["_id"]
    return jsonify(dataset_info)


@app.route("/register_dataset_info", methods=["POST"])
def register_dataset_info():
    dataset_info = request.get_json()
    if not dataset_info_is_valid(dataset_info):
        abort(400)
    i = app.config["mongo_collection"].insert_one(dataset_info).inserted_id
    return str(i)
