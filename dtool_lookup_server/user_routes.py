from flask import (
    abort,
    jsonify,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest.pagination import PaginationParameters

import dtool_lookup_server.utils
import dtool_lookup_server.utils_auth

from dtool_lookup_server.blueprint import Blueprint
from dtool_lookup_server.sort import SortParameters
from dtool_lookup_server.schemas import RegisterUserSchema, UserResponseSchema
from dtool_lookup_server.sql_models import User, UserSchema
from dtool_lookup_server.utils import register_users


bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("/", methods=["GET"])
@bp.sort(sort="+username", allowed_sort_fields=["id", "username", "is_admin"])
@bp.paginate()
@bp.response(200, UserSchema(many=True))
@jwt_required()
def list_users(pagination_parameters: PaginationParameters, sort_parameters: SortParameters):
    """List the users in the dtool lookup server.

    The user in the Authorization token needs to be admin.
    """
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(username):
        abort(404)

    query = User.query.filter_by()
    for sort, order in sort_parameters.sort, sort_parameters.order:
        if field.startswith('-'):
            query = query.order_by(getattr(self.model, field[1:]).desc())
        else:
            query = query.order_by(getattr(self.model, field))
    pagination_parameters.item_count = query.count()
    return query.paginate(
        page=pagination_parameters.page,
        per_page=pagination_parameters.page_size,
        error_out=True
    ).items


@bp.route("/<username>", methods=["GET"])
@bp.response(200, UserResponseSchema)
@jwt_required()
def get_user_info(username):
    """Return a user's information.

    A user can see his/her own profile.
    An admin user can see other user's profiles.
    """
    token_username = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(token_username):
        # Unregistered users should see 404.
        abort(404)

    # Return 404 if the user is not admin and the token username
    # does not match up with the username in the URL.
    if not dtool_lookup_server.utils_auth.has_admin_rights(token_username):
        if token_username != username:
            abort(404)

    return dtool_lookup_server.utils.get_user_info(username)


@bp.route("/users/<username>", methods=["POST"])
@bp.arguments(RegisterUserSchema(many=True, partial=("is_admin",)))
@jwt_required()
def register(data: RegisterUserSchema):
    """Register a user in the dtool lookup server.

    The user in the Authorization token needs to be admin.
    """
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(username):
        abort(404)

    #   # Make it idempotent.
    #   if base_uri_exists(base_uri):
    #       return "", 201

    # There should be some validation of the input here...

    register_users(data)

    return "", 201