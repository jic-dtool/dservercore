from flask import (
    abort,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest import Blueprint

from dtool_lookup_server.sql_models import BaseURISchema, BaseURI
import dtool_lookup_server.utils_auth
from dtool_lookup_server.utils import (
    base_uri_exists,
    register_base_uri,
)

bp = Blueprint("base_uri", __name__, url_prefix="/admin/base_uri")


@bp.route("/register", methods=["POST"])
@bp.arguments(BaseURISchema, required=True)
@jwt_required()
def register(parameter: BaseURISchema):
    """Register a base URI.

    The user needs to be admin.
    """
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(username):
        abort(404)

    # Make it idempotent.
    base_uri = parameter['base_uri']
    if base_uri_exists(base_uri):
        return "", 201

    register_base_uri(base_uri)

    return "", 201


@bp.route("/list", methods=["GET"])
@bp.paginate()
@bp.response(200, BaseURISchema(many=True))
@jwt_required()
def base_uri_list(pagination_parameters):
    """List all base_uris.

    The user needs to be admin.
    """
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(username):
        abort(404)

    query = BaseURI.query.filter_by()
    pagination_parameters.item_count = query.count()
    return query.paginate(
        page=pagination_parameters.page,
        per_page=pagination_parameters.page_size,
        error_out=True
    ).items
