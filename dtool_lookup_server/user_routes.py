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
from dtool_lookup_server.utils import register_user, put_user, patch_user, delete_user


bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
@bp.sort(sort=["+username","-is_admin"], allowed_sort_fields=["id", "username", "is_admin"])
@bp.paginate()
@bp.response(200, UserSchema(many=True))
@jwt_required()
def list_users(pagination_parameters: PaginationParameters, sort_parameters: SortParameters):
    """List the users in the dtool lookup server.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(404)

    query = User.query.filter_by()
    # for sort, order in zip(sort_parameters.sort, sort_parameters.order):
    print(sort_parameters.order())
    #sort, order = sort_parameters.sort, sort_parameters.order
    #print (f"{sort}: {order}")
        #if field.startswith('-'):
        #    query = query.order_by(getattr(self.model, field[1:]).desc())
        #else:
        #    query = query.order_by(getattr(self.model, field))

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
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        # Unregistered users should see 404.
        abort(404)

    # Return 404 if the user is not admin and the token username
    # does not match up with the username in the URL.
    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        if identity != username:
            abort(404)

    return dtool_lookup_server.utils.get_user_info(username)


@bp.route("/<username>", methods=["POST"])
@bp.arguments(RegisterUserSchema(many=False, partial=("username", "is_admin",)))
@jwt_required()
def register(data: RegisterUserSchema, username):
    """Register a user in the dtool lookup server.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(404)

    #   # Make it idempotent.
    #   if base_uri_exists(base_uri):
    #       return "", 201

    # There should be some validation of the input here...

    register_user(username, data)

    return "", 201


@bp.route("/<username>", methods=["PUT"])
@bp.arguments(RegisterUserSchema(many=False, partial=("username", "is_admin",)))
@jwt_required()
def put_update(data: RegisterUserSchema, username):
    """Update a user in the dtool lookup server by replacing entry.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(404)

    put_user(username, data)

    return "", 200


@bp.route("/<username>", methods=["PATCH"])
@bp.arguments(RegisterUserSchema(many=False, partial=("username", "is_admin",)))
@jwt_required()
def patch_update(data: RegisterUserSchema, username):
    """Update a user in the dtool lookup server by patching fields.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(404)

    patch_user(username, data)

    return "", 200


@bp.route("/<username>", methods=["DELETE"])
@jwt_required()
def delete(username):
    """Delete a user from the dtool lookup server.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(404)

    delete_user(username)

    return "", 200
