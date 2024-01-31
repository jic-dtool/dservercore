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

bp = Blueprint("uuids", __name__, url_prefix="/uuids")

@bp.route("/list", methods=["GET"])
@bp.response(200, DatasetSchema(many=True))
@bp.paginate()
@jwt_required()
def list_datasets(pagination_parameters: PaginationParameters):
    """List the datasets a user has access to."""
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)
    datasets = list_datasets_by_user(username)
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
    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)
    datasets = lookup_datasets_by_user_and_uuid(username, uuid)
    pagination_parameters.item_count = len(datasets)
    return jsonify(
        datasets[pagination_parameters.first_item : pagination_parameters.last_item + 1]
    )