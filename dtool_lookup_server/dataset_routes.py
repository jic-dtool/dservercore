from flask import (
    abort,
    Blueprint,
    jsonify,
    request,
    current_app,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from dtool_lookup_server import (
    AuthenticationError,
    AuthorizationError,
    UnknownBaseURIError,
    UnknownURIError,
    ValidationError,
)
from dtool_lookup_server.utils import (
    dataset_info_is_valid,
    get_base_uri_obj,
    get_user_obj,
    summary_of_datasets_by_user,
    list_datasets_by_user,
    lookup_datasets_by_user_and_uuid,
    search_datasets_by_user,
    register_dataset,
    get_manifest_from_uri_by_user,
    get_readme_from_uri_by_user,
    get_annotations_from_uri_by_user,
)


bp = Blueprint("dataset", __name__, url_prefix="/dataset")


@bp.route("/summary", methods=["GET"])
@jwt_required()
def summary_of_datasets():
    """List the dataset a user has access to."""
    username = get_jwt_identity()
    try:
        summary = summary_of_datasets_by_user(username)
    except AuthenticationError:
        abort(401)
    return jsonify(summary)


@bp.route("/list", methods=["GET"])
@jwt_required()
def list_datasets():
    """List the dataset a user has access to."""
    username = get_jwt_identity()
    try:
        datasets = list_datasets_by_user(username)
    except AuthenticationError:
        abort(401)
    return jsonify(datasets)


@bp.route("/lookup/<uuid>", methods=["GET"])
@jwt_required()
def lookup_datasets(uuid):
    """List the dataset a user has access to."""
    username = get_jwt_identity()
    try:
        datasets = lookup_datasets_by_user_and_uuid(username, uuid)
    except AuthenticationError:
        abort(401)
    return jsonify(datasets)


@bp.route("/search", methods=["POST"])
@jwt_required()
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
@jwt_required()
def register():
    """Register a dataset. The user needs to have register permissions."""
    username = get_jwt_identity()
    dataset_info = request.get_json()

    try:
        user = get_user_obj(username)
    except AuthenticationError:
        # User not registered in system.
        abort(401)

    if not dataset_info_is_valid(dataset_info):
        abort(409)

    try:
        base_uri = get_base_uri_obj(dataset_info["base_uri"])
    except ValidationError:
        abort(409)

    if base_uri not in user.register_base_uris:
        abort(401)

    dataset_uri = register_dataset(dataset_info)
    return dataset_uri, 201


@bp.route("/manifest", methods=["POST"])
@jwt_required()
def manifest():
    """Request the dataset manifest."""
    username = get_jwt_identity()
    query = request.get_json()
    if "uri" not in query:
        abort(400)
    uri = query["uri"]

    try:
        manifest = get_manifest_from_uri_by_user(username, uri)
    except AuthenticationError:
        current_app.logger.info("AuthenticaitonError")
        abort(401)
    except AuthorizationError:
        current_app.logger.info("AuthorizationError")
        abort(400)
    except UnknownBaseURIError:
        current_app.logger.info("UnknownBaseURIError")
        abort(400)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(400)

    return jsonify(manifest)


@bp.route("/readme", methods=["POST"])
@jwt_required()
def readme():
    """Request the dataset readme."""
    username = get_jwt_identity()
    query = request.get_json()
    if "uri" not in query:
        abort(400)
    uri = query["uri"]

    try:
        readme = get_readme_from_uri_by_user(username, uri)
    except AuthenticationError:
        current_app.logger.info("AuthenticaitonError")
        abort(401)
    except AuthorizationError:
        current_app.logger.info("AuthorizationError")
        abort(400)
    except UnknownBaseURIError:
        current_app.logger.info("UnknownBaseURIError")
        abort(400)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(400)

    return jsonify(readme)


@bp.route("/annotations", methods=["POST"])
@jwt_required()
def annotations():
    """Request the dataset annotations."""
    username = get_jwt_identity()
    query = request.get_json()
    if "uri" not in query:
        abort(400)
    uri = query["uri"]

    try:
        readme = get_annotations_from_uri_by_user(username, uri)
    except AuthenticationError:
        current_app.logger.info("AuthenticaitonError")
        abort(401)
    except AuthorizationError:
        current_app.logger.info("AuthorizationError")
        abort(400)
    except UnknownBaseURIError:
        current_app.logger.info("UnknownBaseURIError")
        abort(400)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(400)

    return jsonify(readme)
