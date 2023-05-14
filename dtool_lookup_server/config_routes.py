from flask import (
    abort,
    current_app,
    jsonify,
)

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest import Blueprint

import dtool_lookup_server
import dtool_lookup_server.utils_auth
from dtool_lookup_server.utils import versions_to_dict, obj_to_lowercase_key_dict


bp = Blueprint("config", __name__, url_prefix="/config")


@bp.route("/info", methods=["GET"])
@jwt_required()
def server_config():
    """Return the JSON-serialized Flask app configuration."""

    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    return jsonify(obj_to_lowercase_key_dict(
        current_app.config,
        exclusions=current_app.config["CONFIG_SECRETS_TO_OBFUSCATE"]))


@bp.route("/versions", methods=["GET"])
def server_versions():
    """Return the JSON-serialized server component versions.

    This does not require authorization."""

    return jsonify(versions_to_dict())
