"""Routes for user management"""
from flask import (
    abort,
    jsonify,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest.pagination import PaginationParameters

import dservercore.utils
import dservercore.utils_auth

from dservercore.blueprint import Blueprint
from dservercore.sort import SortParameters, ASCENDING, DESCENDING
from dservercore.schemas import SummarySchema
from dservercore.sql_models import User, UserSchema, UserWithPermissionsSchema
from dservercore.utils import register_user, delete_user, summary_of_datasets_by_user


bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("", methods=["GET"])
@bp.sort(sort=["+username"], allowed_sort_fields=["username", "is_admin"])
@bp.paginate()
@bp.response(200, UserWithPermissionsSchema(many=True))
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@jwt_required()
def users_get(pagination_parameters: PaginationParameters, sort_parameters: SortParameters):
    """List the users in dserver.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dservercore.utils_auth.user_exists(identity):
        abort(401)

    if not dservercore.utils_auth.has_admin_rights(identity):
        abort(403)

    order_by_args = []
    for field, order in sort_parameters.order.items():
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
@bp.response(200, UserWithPermissionsSchema)
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def user_get(username):
    """Return a user's information.

    A user can see his/her own profile.
    An admin user can see other user's profiles.
    """
    identity = get_jwt_identity()

    if not dservercore.utils_auth.user_exists(identity):
        abort(401)

    # Return 403 if the user is not admin and the token username
    # does not match up with the username in the URL.
    if not dservercore.utils_auth.has_admin_rights(identity):
        if identity != username:
            abort(403)

    if not dservercore.utils_auth.user_exists(username):
        abort(404)

    return dservercore.utils.get_user_info(username)


@bp.route("/<username>", methods=["PUT"])
@bp.arguments(UserSchema)
@bp.response(200)
@bp.alt_response(201, description="Created")
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@jwt_required()
def user_put(data: UserSchema, username):
    """Create or update a user in dserver by replacing entry.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dservercore.utils_auth.user_exists(identity):
        abort(401)

    if not dservercore.utils_auth.has_admin_rights(identity):
        abort(403)

    success_code = 201  # create
    if dservercore.utils_auth.user_exists(username):
        success_code = 200  # update

    register_user(username, data)

    return "", success_code


@bp.route("/<username>", methods=["DELETE"])
@bp.response(200)
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@jwt_required()
def user_delete(username):
    """Delete a user from dserver.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dservercore.utils_auth.user_exists(identity):
        abort(401)

    if not dservercore.utils_auth.has_admin_rights(identity):
        abort(403)

    delete_user(username)

    return "", 200


@bp.route("/<username>/summary", methods=["GET"])
@bp.response(200, SummarySchema)
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def user_summary_get(username):
    """Global summary of the datasets a user has access to."""
    identity = get_jwt_identity()

    if not dservercore.utils_auth.user_exists(identity):
        # Authenticated user does not exist
        abort(401)

    # Return 403 if the user is not admin and the token username
    # does not match up with the username in the URL.
    if not dservercore.utils_auth.has_admin_rights(identity):
        if identity != username:
            abort(403)

    if not dservercore.utils_auth.user_exists(username):
        # Authenticated user is admin, but user summary requested does not exist
        abort(404)

    summary = summary_of_datasets_by_user(username)
    return summary