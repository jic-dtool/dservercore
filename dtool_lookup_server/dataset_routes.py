from flask import (
    abort,
    Blueprint,
    jsonify
)
from flask_jwt_extended import jwt_required, get_jwt_identity

from dtool_lookup_server.utils import list_datasets_by_user

bp = Blueprint("dataset", __name__, url_prefix="/dataset")


@bp.route("/list", methods=["GET"])
@jwt_required
def list_datasets():
    """List the dataset a user has access to."""
    username = get_jwt_identity()
    datasets = list_datasets_by_user(username)
    if datasets is None:
        abort(401)
    return jsonify(datasets)
