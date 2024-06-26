"""Routes for querying dataset entries by their UUIDs"""
from flask import (
    abort,
    jsonify
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from flask_smorest.pagination import PaginationParameters

from dservercore.blueprint import Blueprint
from dservercore.sort import SortParameters
from dservercore.sql_models import DatasetSchema
import dservercore.utils_auth
from dservercore.utils import (
    lookup_datasets_by_user_and_uuid,
    DATASET_SORT_FIELDS
)


bp = Blueprint("uuids", __name__, url_prefix="/uuids")


@bp.route("/<uuid>", methods=["GET"])
@bp.sort(sort=["+uri"], allowed_sort_fields=DATASET_SORT_FIELDS)
@bp.paginate()
@bp.response(200, DatasetSchema(many=True))
@bp.alt_response(401, description="Not registered")
@jwt_required()
def uuid_get(pagination_parameters: PaginationParameters,
                    sort_parameters: SortParameters, uuid):
    """List all instances of a dataset in any base_uris the user has access to."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    datasets = lookup_datasets_by_user_and_uuid(username, uuid,
                                                pagination_parameters=pagination_parameters,
                                                sort_parameters=sort_parameters)

    return datasets
