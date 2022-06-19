from flask import (
    abort,
    jsonify,
    current_app,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from flask_smorest import Blueprint
from flask_smorest.pagination import PaginationParameters

from .sql_models import (
    BaseURISchema,
    DatasetSchema
)

from marshmallow.fields import (
    String,
    Dict
)

from dtool_lookup_server import (
    AuthenticationError,
    AuthorizationError,
    UnknownBaseURIError,
    UnknownURIError,
    ValidationError,
)
from dtool_lookup_server.schemas import (
    UriSchema,
    RegisterDatasetSchema,
    SearchDatasetSchema,
    SummarySchema,
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
@bp.response(200, SummarySchema)
@jwt_required()
def summary_of_datasets():
    """Global summary of the datasets a user has access to."""
    username = get_jwt_identity()
    try:
        summary = summary_of_datasets_by_user(username)
    except AuthenticationError:
        abort(401)
    return summary


@bp.route("/list", methods=["GET"])
@bp.response(200, DatasetSchema(many=True))
@bp.paginate()
@jwt_required()
def list_datasets(pagination_parameters: PaginationParameters):
    """List the datasets a user has access to."""
    username = get_jwt_identity()
    try:
        datasets = list_datasets_by_user(username)
    except AuthenticationError:
        abort(401)
    pagination_parameters.item_count = len(datasets)
    return jsonify(
        datasets[pagination_parameters.first_item : pagination_parameters.last_item + 1]
    )


@bp.route("/lookup/<uuid>", methods=["GET"])
@bp.response(200, DatasetSchema(many=True))
@bp.paginate()
@jwt_required()
def lookup_datasets(pagination_parameters: PaginationParameters, uuid):
    """List all instances of a dataset in any base_uris the user has access to."""
    username = get_jwt_identity()
    try:
        datasets = lookup_datasets_by_user_and_uuid(username, uuid)
    except AuthenticationError:
        abort(401)
    pagination_parameters.item_count = len(datasets)
    return jsonify(
        datasets[pagination_parameters.first_item : pagination_parameters.last_item + 1]
    )


@bp.route("/search", methods=["POST"])
@bp.arguments(SearchDatasetSchema(partial=True))
@bp.response(200, DatasetSchema(many=True))
@bp.paginate()
@jwt_required()
def search_datasets(
    query: SearchDatasetSchema, pagination_parameters: PaginationParameters
):
    """List datasets the user has access to matching the query."""
    username = get_jwt_identity()
    try:
        datasets = search_datasets_by_user(username, query)
    except AuthenticationError:
        abort(401)
    pagination_parameters.item_count = len(datasets)
    return jsonify(
        datasets[pagination_parameters.first_item : pagination_parameters.last_item + 1]
    )


@bp.route("/register", methods=["POST"])
@bp.arguments(RegisterDatasetSchema(partial=("created_at",)))
@bp.response(201, UriSchema)
@jwt_required()
def register(dataset: RegisterDatasetSchema):
    """Register a dataset. The user needs to have register permissions on the base_uri."""
    username = get_jwt_identity()
    dataset_info = dataset

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
    return {"uri": dataset_uri}


@bp.route("/manifest", methods=["POST"])
@bp.arguments(UriSchema)
@jwt_required()
def manifest(query: UriSchema):
    """Request the dataset manifest."""
    username = get_jwt_identity()
    if "uri" not in query:
        abort(400)
    uri = query["uri"]

    try:
        manifest_ = get_manifest_from_uri_by_user(username, uri)
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

    return jsonify(manifest_)


@bp.route("/readme", methods=["POST"])
@bp.arguments(UriSchema)
@jwt_required()
def readme(query: UriSchema):
    """Request the dataset readme."""
    username = get_jwt_identity()
    if "uri" not in query:
        abort(400)
    uri = query["uri"]

    try:
        readme_ = get_readme_from_uri_by_user(username, uri)
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

    return jsonify(readme_)


@bp.route("/annotations", methods=["POST"])
@bp.arguments(UriSchema)
@bp.response(200, Dict)
@jwt_required()
def annotations(query: UriSchema):
    """Request the dataset annotations."""
    username = get_jwt_identity()
    if "uri" not in query:
        abort(400)
    uri = query["uri"]

    try:
        annotations_ = get_annotations_from_uri_by_user(username, uri)
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

    return jsonify(annotations_)
