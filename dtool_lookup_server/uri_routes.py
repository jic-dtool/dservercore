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
    URISchema,
    RegisterDatasetSchema,
    SearchDatasetSchema,
    SummarySchema,
)
import dtool_lookup_server.utils_auth
from dtool_lookup_server.utils import (
    dataset_info_is_valid,
    summary_of_datasets_by_user,
    list_datasets_by_user,
    search_datasets_by_user,
    register_dataset
)

bp = Blueprint("uris", __name__, url_prefix="/uris")

DATASET_SORT_FIELDS = [
    "base_uri",
    "created_at",
    "creator_username",
    "frozen_at",
    "name",
    "uri",
    "uuid"
]


@bp.route("/summary", methods=["GET"])
@bp.response(200, SummarySchema)
@jwt_required()
def summary_of_datasets():
    """Global summary of the datasets a user has access to."""
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)
    summary = summary_of_datasets_by_user(username)
    return summary


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


@bp.route("/register", methods=["POST"])
@bp.arguments(RegisterDatasetSchema(partial=("created_at",)))
@bp.response(201, URISchema)
@jwt_required()
def register(dataset: RegisterDatasetSchema):
    """Register a dataset. The user needs to have register permissions on the base_uri."""
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    if not dataset_info_is_valid(dataset):
        abort(409)

    if not dtool_lookup_server.utils_auth.may_register(username, dataset["base_uri"]):
        abort(401)

    dataset_uri = register_dataset(dataset)
    return {"uri": dataset_uri}