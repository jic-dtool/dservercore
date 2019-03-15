from flask import (
    abort,
    Blueprint,
    current_app,
    request,
    jsonify
)
import jwt

from dtool_lookup_server.utils import list_datasets_by_user

bp = Blueprint("dataset", __name__, url_prefix="/dataset")

@bp.route("/list", methods=["POST"])
def list_datasets():
    """List the dataset a user has access to."""
    data = request.get_json()
    token = data["token"]
    payload = jwt.decode(
        token,
        current_app.config["JWT_PUBLIC_KEY"],
        algorithms=['RS256'])
    username = payload["username"]
    datasets = list_datasets_by_user(username)
    if datasets is None:
        abort(401)
    return jsonify(datasets)
