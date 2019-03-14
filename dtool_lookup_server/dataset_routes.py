from flask import Blueprint, jsonify

bp = Blueprint("dataset", __name__, url_prefix="/dataset")

@bp.route("/list", methods=["POST"])
def list_datasets_by_user():
    """List the dataset a user has access to."""
    return jsonify({})
