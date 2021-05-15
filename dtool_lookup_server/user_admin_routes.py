from flask import (
    abort,
    Blueprint,
    jsonify,
    request,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from dtool_lookup_server import (
    AuthenticationError,
)
import dtool_lookup_server.utils
from dtool_lookup_server.utils import (
    get_user_obj,
    register_users,
)

bp = Blueprint("user_admin", __name__, url_prefix="/admin/user")


@bp.route("/register", methods=["POST"])
@jwt_required()
def register():
    """Register a user in the dtool lookup server.

    The user in the Authorization token needs to be admin. Returns 404 for
    non-admins.
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
@jwt_required()
def list_users():
    """List the users in the dtool lookup server.

    The user in the Authorization token needs to be admin. Returns 404 for
    non-admins.
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

    return jsonify(dtool_lookup_server.utils.list_users())
