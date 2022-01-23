from flask import (
    abort,
    request,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest import Blueprint

from dtool_lookup_server import (
    AuthenticationError,
)
from dtool_lookup_server.schemas import BaseUriSchema
from dtool_lookup_server.utils import (
    base_uri_exists,
    get_user_obj,
    register_base_uri,
)

bp = Blueprint("base_uri", __name__, url_prefix="/admin/base_uri")


@bp.route("/register", methods=["POST"])
@bp.arguments(BaseUriSchema)
@jwt_required()
def register(uri: BaseUriSchema):
    """Register a base URI.

    The user needs to be admin.
    """
    username = get_jwt_identity()
    data = request.get_json()

    base_uri = data["base_uri"]

    try:
        user = get_user_obj(username)
    except AuthenticationError:
        # Unregistered users should see 404.
        abort(404)

    # Non admin users should see 404.
    if not user.is_admin:
        abort(404)

    # Make it idempotent.
    if base_uri_exists(base_uri):
        return "", 201

    register_base_uri(base_uri)

    return "", 201


from dtool_lookup_server.sql_models import BaseURISchema, BaseURI


@bp.route("/list", methods=["GET"])
@bp.paginate()
@bp.response(200, BaseURISchema(many=True))
@jwt_required()
def base_uri_list(pagination_parameters):
    """List all base_uris.

    The user needs to be admin.
    """
    username = get_jwt_identity()
    try:
        user = get_user_obj(username)
    except AuthenticationError:
        # Unregistered users should see 404.
        abort(404)
    # Non admin users should see 404.
    if not user.is_admin:
        abort(404)

    query = BaseURI.query.filter_by()
    pagination_parameters.item_count = query.count()
    return query.paginate(
        pagination_parameters.page, pagination_parameters.page_size, True
    ).items
