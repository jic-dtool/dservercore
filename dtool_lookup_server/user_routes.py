from flask import (
    abort,
    jsonify,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest import Blueprint

from dtool_lookup_server import AuthenticationError
import dtool_lookup_server.utils
import dtool_lookup_server.utils_auth

from .schemas import UserResponseSchema

bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/info/<username>", methods=["GET"])
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
