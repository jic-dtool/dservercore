from flask import (
    abort,
    jsonify,
    current_app,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from flask_smorest.pagination import PaginationParameters

from dtool_lookup_server.blueprint import Blueprint
from dtool_lookup_server.sort import SortParameters, ASCENDING, DESCENDING
from dtool_lookup_server.sql_models import DatasetSchema
from dtool_lookup_server.schemas import (
    RegisterDatasetSchema,
    SearchDatasetSchema
)
import dtool_lookup_server.utils_auth
from dtool_lookup_server.utils import (
    dataset_info_is_valid,
    list_datasets_by_user,
    search_datasets_by_user,
    get_dataset_by_user_and_uri,
    register_dataset,
    url_suffix_to_uri,
    DATASET_SORT_FIELDS
)

bp = Blueprint("uris", __name__, url_prefix="/uris")


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
@bp.sort(sort=["+uri"], allowed_sort_fields=DATASET_SORT_FIELDS)
@bp.paginate()
@bp.response(200, DatasetSchema(many=True))
@jwt_required()
def list_datasets(pagination_parameters: PaginationParameters,
                  sort_parameters: SortParameters):
    """List the datasets a user has access to."""
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)
    datasets = list_datasets_by_user(username,
                                     pagination_parameters=pagination_parameters,
                                     sort_parameters=sort_parameters)

    return datasets


@bp.route("/search", methods=["POST"])
@bp.arguments(SearchDatasetSchema(partial=True))
@bp.response(200, DatasetSchema(many=True))
@bp.paginate()
@bp.alt_response(401, "User not registered")
@jwt_required()
def search_datasets(
    query: SearchDatasetSchema, pagination_parameters: PaginationParameters
):
    """List datasets the user has access to matching the query."""
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)
    datasets = search_datasets_by_user(username, query)
    pagination_parameters.item_count = len(datasets)
    return jsonify(
        datasets[pagination_parameters.first_item : pagination_parameters.last_item + 1]
    )


@bp.route("/<path:uri>", methods=["GET"])
@bp.response(200, DatasetSchema)
@bp.alt_response(401, "User not registered")
@bp.alt_response(403, "User has no permissions to search base URI")
@bp.alt_response(404, "Dataset entry does not exist")
@jwt_required()
def get_dataset_by_uri(uri):
    """Return dataset information by URI."""
    username = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    uri = url_suffix_to_uri(uri)

    if not dtool_lookup_server.utils_auth.may_access(username, uri):
        # registered users without search rights on base uri should see 403.
        abort(403)

    dataset = get_dataset_by_user_and_uri(username, uri)

    if dataset is None:
        abort(404)

    return dataset


@bp.route("/<path:uri>", methods=["POST"])
@bp.arguments(RegisterDatasetSchema(partial=("created_at",)))
@bp.response(201)
@bp.alt_response(401, "User not registered")
@bp.alt_response(409, "Dataset information not valid")
@jwt_required()
def register(dataset: RegisterDatasetSchema, uri):
    """Register a dataset.

    The user needs to have register permissions on the base_uri."""
    username = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    uri = url_suffix_to_uri(uri)

    if not uri == dataset["uri"]:
        abort(409)

    if not dataset_info_is_valid(dataset):
        abort(409)

    if not dtool_lookup_server.utils_auth.may_register(username, dataset["base_uri"]):
        abort(401)

    dataset_uri = register_dataset(dataset)
    # return {"uri": dataset_uri}
    return "", 201


@bp.route("/<path:uri>", methods=["PUT"])
@bp.arguments(RegisterDatasetSchema(partial=("created_at",)))
@jwt_required()
def put_update(dataset : RegisterDatasetSchema, uri):
    """Update a dataset entry in the dtool lookup server by replacing entry.

    The user needs to have register permissions on the base_uri.
    """
    identity = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(404)

    uri = url_suffix_to_uri(uri)

    # PUT

    return "", 200


@bp.route("/<path:base_uri>", methods=["PATCH"])
@bp.arguments(RegisterDatasetSchema(partial=("created_at",)))
@jwt_required()
def patch_update(dataset : RegisterDatasetSchema, uri):
    """Update a dataset entry in the dtool lookup server by patching fields.

    The user needs to have register permissions on the base_uri.
    """
    identity = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(404)

    uri = url_suffix_to_uri(uri)

    # PATCH

    return "", 200


@bp.route("/<path:base_uri>", methods=["DELETE"])
@jwt_required()
def delete(uri):
    """Delete a dataset entry from the dtool lookup server.

    The user needs to have register permissions on the base_uri.
    """
    identity = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(404)

    uri = url_suffix_to_uri(uri)

    # DELETE

    return "", 200
