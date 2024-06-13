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

from dservercore import ValidationError, UnknownURIError
from dservercore.blueprint import Blueprint
from dservercore.sort import SortParameters, ASCENDING, DESCENDING
from dservercore.sql_models import DatasetSchema
from dservercore.schemas import (
    RegisterDatasetSchema,
    SearchDatasetSchema
)
import dservercore.utils_auth
from dservercore.utils import (
    dataset_info_is_valid,
    list_datasets_by_user,
    search_datasets_by_user,
    get_dataset_by_user_and_uri,
    register_dataset,
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
def uris_get(query: SearchDatasetSchema,
                    pagination_parameters: PaginationParameters,
                    sort_parameters: SortParameters):
    """Search the datasets a user has access to."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
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
def uris_post(query: SearchDatasetSchema,
                   pagination_parameters: PaginationParameters,
                   sort_parameters: SortParameters):
    """Search the datasets a user has access to."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
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
def uri_get(uri):
    """Return dataset information by URI."""
    username = get_jwt_identity()

    if not dservercore.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    uri = url_suffix_to_uri(uri)

    if not dservercore.utils_auth.may_access(username, uri):
        # registered users without search rights on base uri should see 403.
        abort(403)

    dataset = get_dataset_by_user_and_uri(username, uri)

    if dataset is None:
        abort(404)

    return dataset


@bp.route("/<path:uri>", methods=["PUT"])
@bp.arguments(RegisterDatasetSchema(partial=("created_at",)))
@bp.response(200)
@bp.alt_response(201, description="Created")
@bp.alt_response(400, description="Dataset not valid")
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def uri_put(dataset : RegisterDatasetSchema, uri):
    """Update a dataset entry in dserver by replacing entry.

    The user needs to have register permissions on the base_uri.
    """
    identity = get_jwt_identity()

    if not dservercore.utils_auth.user_exists(identity):
        # Unregistered users should see 401.
        abort(401)

    if not dservercore.utils_auth.may_register(identity, dataset["base_uri"]):
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


@bp.route("/<path:uri>", methods=["DELETE"])
@bp.response(200)
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@jwt_required()
def uri_delete(uri):
    """Delete a dataset entry from dserver.

    The user needs to have register permissions on the base_uri.
    """
    identity = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(identity):
        abort(401)

    uri = url_suffix_to_uri(uri)

    base_uri_str = uri.rsplit("/", 1)[0]

    if not dservercore.utils_auth.may_register(identity, base_uri_str):
        abort(403)

    try:
        dataset_uri = delete_dataset(uri)
    except ValidationError as message:
        abort(400, message)

    return "", 200
