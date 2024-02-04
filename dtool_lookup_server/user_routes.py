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
from dtool_lookup_server.sort import SortParameters, ASCENDING, DESCENDING
from dtool_lookup_server.schemas import RegisterUserSchema, UserResponseSchema, SummarySchema
from dtool_lookup_server.sql_models import User, UserSchema
from dtool_lookup_server.utils import register_user, put_user, patch_user, delete_user, summary_of_datasets_by_user


bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
@bp.sort(sort=["+id"], allowed_sort_fields=["id", "username", "is_admin"])
@bp.paginate()
@bp.response(200, UserSchema(many=True))
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@jwt_required()
def list_users(pagination_parameters: PaginationParameters, sort_parameters: SortParameters):
    """List the users in the dtool lookup server.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(403)

    order_by_args = []
    for field, order in sort_parameters.order().items():
        if not hasattr(User, field):
            continue
        if order == DESCENDING:
            order_by_args.append(getattr(User, field).desc())
        else:  # ascending
            order_by_args.append(getattr(User, field))

    query = User.query.order_by(*order_by_args).filter_by()
    pagination_parameters.item_count = query.count()
    return query.paginate(
        page=pagination_parameters.page,
        per_page=pagination_parameters.page_size,
        error_out=True
    ).items


@bp.route("/<username>", methods=["GET"])
@bp.response(200, UserResponseSchema)
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@bp.alt_response(404, "Not found")
@jwt_required()
def get_user_info(username):
    """Return a user's information.

    A user can see his/her own profile.
    An admin user can see other user's profiles.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    # Return 403 if the user is not admin and the token username
    # does not match up with the username in the URL.
    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        if identity != username:
            abort(403)

    if not dtool_lookup_server.utils_auth.user_exists(username):
        abort(404)

    return dtool_lookup_server.utils.get_user_info(username)


@bp.route("/<username>", methods=["POST"])
@bp.arguments(RegisterUserSchema(many=False, partial=("username", "is_admin",)))
@bp.response(201)
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@jwt_required()
def register(data: RegisterUserSchema, username):
    """Register a user in the dtool lookup server.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(403)

    register_user(username, data)

    return "", 201


@bp.route("/<username>", methods=["PUT"])
@bp.arguments(RegisterUserSchema(many=False, partial=("username", "is_admin",)))
@bp.response(200)
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@bp.alt_response(404, "Not found")
@jwt_required()
def put_update(data: RegisterUserSchema, username):
    """Update a user in the dtool lookup server by replacing entry.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(403)

    if not dtool_lookup_server.utils_auth.user_exists(username):
        abort(404)

    put_user(username, data)

    return "", 200


@bp.route("/<username>", methods=["PATCH"])
@bp.arguments(RegisterUserSchema(many=False, partial=("username", "is_admin",)))
@bp.response(200)
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@jwt_required()
def patch_update(data: RegisterUserSchema, username):
    """Update a user in the dtool lookup server by patching fields.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(403)

    patch_user(username, data)

    return "", 200


@bp.route("/<username>", methods=["DELETE"])
@bp.response(200)
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@jwt_required()
def delete(username):
    """Delete a user from the dtool lookup server.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(403)

    delete_user(username)

    return "", 200


@bp.route("/<username>/summary", methods=["GET"])
@bp.response(200, SummarySchema)
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@bp.alt_response(404, "Not found")
@jwt_required()
def summary_of_datasets(username):
    """Global summary of the datasets a user has access to."""
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        # Authenticated user does not exist
        abort(401)

    # Return 403 if the user is not admin and the token username
    # does not match up with the username in the URL.
    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        if identity != username:
            abort(403)

    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Authenticated user is admin, but user summary requested does not exist
        abort(404)

    summary = summary_of_datasets_by_user(username)
    return summary