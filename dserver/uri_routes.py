"""Routes for querying and managing dataset entries by their URIs"""
from flask import (
    abort,
    jsonify
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from flask_smorest.pagination import PaginationParameters

from dserver import ValidationError, UnknownURIError
from dserver.blueprint import Blueprint
from dserver.sort import SortParameters, ASCENDING, DESCENDING
from dserver.sql_models import DatasetSchema
from dserver.schemas import (
    RegisterDatasetSchema,
    SearchDatasetSchema
)
import dserver.utils_auth
from dserver.utils import (
    dataset_info_is_valid,
    list_datasets_by_user,
    search_datasets_by_user,
    get_dataset_by_user_and_uri,
    register_dataset,
    put_update_dataset,
    patch_update_dataset,
    delete_dataset,
    dataset_uri_exists,
    url_suffix_to_uri,
    DATASET_SORT_FIELDS
)

bp = Blueprint("uris", __name__, url_prefix="/uris")


@bp.route("", methods=["GET"])
@bp.arguments(SearchDatasetSchema, location="query")
@bp.sort(sort=["+uri"], allowed_sort_fields=DATASET_SORT_FIELDS)
@bp.paginate()
@bp.response(200, DatasetSchema(many=True))
@bp.alt_response(401, description="Not registered")
@jwt_required()
def search_datasets(query: SearchDatasetSchema,
                    pagination_parameters: PaginationParameters,
                    sort_parameters: SortParameters):
    """Search the datasets a user has access to."""
    username = get_jwt_identity()
    if not dserver.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    if len(query) == 0:
        # here, the data source is the dserver-internal sql database
        datasets = list_datasets_by_user(username,
                                         pagination_parameters=pagination_parameters,
                                         sort_parameters=sort_parameters)
    else:
        # here, the data source is the search plugin
        datasets = search_datasets_by_user(username, query,
                                           pagination_parameters=pagination_parameters,
                                           sort_parameters=sort_parameters)

    return datasets


# We offer search via post method as well in case the URL-embedded query string
# does not suffice for formulating a complex search query.
@bp.route("", methods=["POST"])
@bp.arguments(SearchDatasetSchema)
@bp.sort(sort=["+uri"], allowed_sort_fields=DATASET_SORT_FIELDS)
@bp.paginate()
@bp.response(200, DatasetSchema(many=True))
@bp.alt_response(401, description="Not registered")
@jwt_required()
def search_datasets(query: SearchDatasetSchema,
                   pagination_parameters: PaginationParameters,
                   sort_parameters: SortParameters):
    """Search the datasets a user has access to."""
    username = get_jwt_identity()
    if not dserver.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    if len(query) == 0:
        # here, the data source is the dserver-internal sql database
        datasets = list_datasets_by_user(username,
                                         pagination_parameters=pagination_parameters,
                                         sort_parameters=sort_parameters)
    else:
        # here, the data source is the search plugin
        datasets = search_datasets_by_user(username, query,
                                           pagination_parameters=pagination_parameters,
                                           sort_parameters=sort_parameters)

    return datasets


@bp.route("/<path:uri>", methods=["GET"])
@bp.response(200, DatasetSchema)
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def get_dataset_by_uri(uri):
    """Return dataset information by URI."""
    username = get_jwt_identity()

    if not dserver.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    uri = url_suffix_to_uri(uri)

    if not dserver.utils_auth.may_access(username, uri):
        # registered users without search rights on base uri should see 403.
        abort(403)

    dataset = get_dataset_by_user_and_uri(username, uri)

    if dataset is None:
        abort(404)

    return dataset


@bp.route("/<path:uri>", methods=["POST"])
@bp.arguments(RegisterDatasetSchema(partial=("created_at",)))
@bp.response(201)
@bp.alt_response(200, description="Updated")
@bp.alt_response(400, description="Dataset not valid")
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@jwt_required()
def register(dataset: RegisterDatasetSchema, uri):
    """Register a dataset.

    The user needs to have register permissions on the base_uri."""
    identity = get_jwt_identity()

    if not dserver.utils_auth.user_exists(identity):
        # Unregistered users should see 401.
        abort(401)

    if not dserver.utils_auth.may_register(identity, dataset["base_uri"]):
        abort(403)

    uri = url_suffix_to_uri(uri)

    if not uri == dataset["uri"]:
        abort(400)

    if not dataset_info_is_valid(dataset):
        abort(400)

    success_code = 201  # created
    if dataset_uri_exists(uri):
        success_code = 200  # updated

    try:
        dataset_uri = register_dataset(dataset)
    except ValidationError as message:
        # this should only be reached if plugins fail with a validation error
        abort(400, message)

    return "", success_code


@bp.route("/<path:uri>", methods=["PUT"])
@bp.arguments(RegisterDatasetSchema(partial=("created_at",)))
@bp.response(200)
@bp.alt_response(201, description="Created")
@bp.alt_response(400, description="Dataset not valid")
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def put_update(dataset : RegisterDatasetSchema, uri):
    """Update a dataset entry in the dtool lookup server by replacing entry.

    The user needs to have register permissions on the base_uri.
    """
    identity = get_jwt_identity()

    if not dserver.utils_auth.user_exists(identity):
        # Unregistered users should see 401.
        abort(401)

    if not dserver.utils_auth.may_register(identity, dataset["base_uri"]):
        abort(403)

    uri = url_suffix_to_uri(uri)

    if not uri == dataset["uri"]:
        abort(400)

    if not dataset_info_is_valid(dataset):
        abort(400)

    success_code = 201  # created
    if dataset_uri_exists(uri):
        success_code = 200  # updated

    try:
        dataset_uri = put_update_dataset(dataset)
    except ValidationError as message:
        # this should only be reached if plugins fail with a validation error
        abort(400, message)

    return "", success_code


@bp.route("/<path:uri>", methods=["PATCH"])
@bp.arguments(RegisterDatasetSchema(partial=("created_at",)))
@bp.response(200)
@bp.alt_response(400, description="Dataset not valid")
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def patch_update(dataset : RegisterDatasetSchema, uri):
    """Update a dataset entry in the dtool lookup server by patching fields.

    The user needs to have register permissions on the base_uri.
    """
    identity = get_jwt_identity()

    if not dserver.utils_auth.user_exists(identity):
        # Unregistered users should see 401.
        abort(401)

    uri = url_suffix_to_uri(uri)

    # infer base URI, if not provided
    # import pdb; pdb.set_trace()
    if "base_uri" in dataset:
        base_uri = dataset["base_uri"]
    else:
        base_uri = uri.rsplit("/", 1)[0]

    if not dserver.utils_auth.may_register(identity, base_uri):
        abort(403)

    if not uri == dataset["uri"]:
        abort(400)

    # no validation of dataset info, only partial

    try:
        dataset_uri = patch_update_dataset(dataset)
    except ValidationError as message:
        # this should only be reached if plugins fail with a validation error
        abort(400, message)  # invalid data
    except UnknownURIError as message:
        abort(404, message)  # not found

    return "", 200


@bp.route("/<path:uri>", methods=["DELETE"])
@bp.response(200)
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@jwt_required()
def delete(uri):
    """Delete a dataset entry from the dtool lookup server.

    The user needs to have register permissions on the base_uri.
    """
    identity = get_jwt_identity()
    if not dserver.utils_auth.user_exists(identity):
        abort(401)

    uri = url_suffix_to_uri(uri)

    base_uri_str = uri.rsplit("/", 1)[0]

    if not dserver.utils_auth.may_register(identity, base_uri_str):
        abort(403)

    try:
        dataset_uri = delete_dataset(uri)
    except ValidationError as message:
        abort(400, message)

    return "", 200
