from flask import Blueprint, request, jsonify, abort, render_template

from dtool_lookup_server import mongo, utils

bp = Blueprint("legacy", __name__, url_prefix=None)

@bp.route("/")
def index():
    num_datasets = mongo.db.datasets.count()
    return render_template("index.html", num_datasets=num_datasets)


@bp.route("/lookup_datasets/<uuid>")
def lookup_datasets(uuid):
    datasets = utils.lookup_datasets(
        mongo.db.datasets,
        uuid
    )
    return jsonify(datasets)


@bp.route("/register_dataset", methods=["POST"])
def register_dataset():
    dataset_info = request.get_json()
    uuid = utils.register_dataset(
        mongo.db.datasets,
        dataset_info
    )
    if uuid is None:
        abort(400)
    return uuid


@bp.route("/search_for_datasets", methods=["POST"])
def search_for_datasets():
    query = request.get_json()
    print(query)
    datasets = utils.search_for_datasets(
        mongo.db.datasets,
        query
    )
    print("datasets in route {}".format(datasets))
    return jsonify(datasets)
