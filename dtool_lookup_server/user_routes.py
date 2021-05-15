from flask import (
    abort,
    Blueprint,
    jsonify,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from dtool_lookup_server import AuthenticationError
import dtool_lookup_server.utils
bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/info/<username>", methods=["GET"])
@jwt_required()
def get_user_info(username):
    """Return a users information.

    A user can see his/her own profile.
    An admin user can see other user's profiles.
    A user who tries to see another user's profile gets a 404.
    """
    token_username = get_jwt_identity()

    try:
        user = dtool_lookup_server.utils.get_user_obj(token_username)
    except AuthenticationError:
        # Unregistered users should see 404.
        abort(404)

    # Return 404 if the user is not admin and the token username
    # does not match up with the username in the URL.
    if not user.is_admin:
        if token_username != username:
            abort(404)

    return jsonify(dtool_lookup_server.utils.get_user_info(username))
