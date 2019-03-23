from flask import (
    abort,
    Blueprint,
    jsonify,
    request,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from dtool_lookup_server import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
)
from dtool_lookup_server.utils import (
    list_datasets_by_user,
    search_datasets_by_user,
    register_dataset,
)

bp = Blueprint("dataset", __name__, url_prefix="/dataset")


@bp.route("/list", methods=["GET"])
@jwt_required
def list_datasets():
    """List the dataset a user has access to."""
    username = get_jwt_identity()
    try:
        datasets = list_datasets_by_user(username)
    except AuthenticationError:
        abort(401)
    return jsonify(datasets)


@bp.route("/search", methods=["POST"])
@jwt_required
def search_datasets():
    """List the dataset a user has access to."""
    username = get_jwt_identity()
    query = request.get_json()
    try:
        datasets = search_datasets_by_user(username, query)
    except AuthenticationError:
        abort(401)
    return jsonify(datasets)


@bp.route("/register", methods=["POST"])
@jwt_required
def register():
    """Register a dataset. The user needs to have register permissions."""
    username = get_jwt_identity()
    dataset_info = request.get_json()

    try:
        register_dataset(username, dataset_info)
    except AuthenticationError:
        abort(401)
    except AuthorizationError:
        abort(401)
    except ValidationError:
        abort(400)
    return "", 201
