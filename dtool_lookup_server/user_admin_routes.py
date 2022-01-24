from flask import (
    abort,
    request,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest import Blueprint
from flask_smorest.pagination import PaginationParameters

from dtool_lookup_server import (
    AuthenticationError,
)

from dtool_lookup_server.schemas import RegisterUserSchema
from dtool_lookup_server.sql_models import (
    User,
    UserSchema
)
from dtool_lookup_server.utils import (
    get_user_obj,
    register_users,
)

bp = Blueprint("user_admin", __name__, url_prefix="/admin/user")


@bp.route("/register", methods=["POST"])
@bp.arguments(RegisterUserSchema(many=True, partial=("is_admin",)))
@jwt_required()
def register(user: RegisterUserSchema):
    """Register a user in the dtool lookup server.

    The user in the Authorization token needs to be admin.
    """
    username = get_jwt_identity()
    data = request.get_json()

    try:
        user = get_user_obj(username)
    except AuthenticationError:
        # Unregistered users should see 404.
        abort(404)

    # Non admin users should see 404.
    if not user.is_admin:
        abort(404)

    #   # Make it idempotent.
    #   if base_uri_exists(base_uri):
    #       return "", 201

    # There should be some validation of the input here...

    register_users(data)

    return "", 201


@bp.route("/list", methods=["GET"])
@bp.paginate()
@bp.response(200, UserSchema(many=True))
@jwt_required()
def list_users(pagination_parameters: PaginationParameters):
    """List the users in the dtool lookup server.

    The user in the Authorization token needs to be admin.
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
    query = User.query.filter_by()
    pagination_parameters.item_count = query.count()
    return query.paginate(
        pagination_parameters.page, pagination_parameters.page_size, True
    ).items
