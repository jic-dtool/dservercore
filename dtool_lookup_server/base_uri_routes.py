from flask import (
    abort,
    Blueprint,
    request,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from dtool_lookup_server import (
    AuthenticationError,
)
from dtool_lookup_server.utils import (
    base_uri_exists,
    get_user_obj,
    register_base_uri,
)

bp = Blueprint("base_uri", __name__, url_prefix="/base_uri")


@bp.route("/register", methods=["POST"])
@jwt_required
def register():
    """Register a base URI.

    The user needs to be admin. Returns 404 for non-admins.
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

    register_base_uri("s3://snow-white-again")

    return "", 201
