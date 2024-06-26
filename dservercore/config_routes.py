"""Routes for retrieving server and server-side plugin configuration"""
from flask import (
    abort,
    current_app,
    jsonify,
)

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

import dservercore
import dservercore.utils_auth
from dservercore.blueprint import Blueprint
from dservercore.schemas import ConfigSchema, VersionSchema
from dservercore.utils import versions_to_dict, obj_to_lowercase_key_dict


bp = Blueprint("config", __name__, url_prefix="/config")


@bp.route("/info", methods=["GET"])
@bp.response(200, ConfigSchema)
@bp.alt_response(401, description="Not registered")
@jwt_required()
def server_config():
    """Return the JSON-serialized Flask app configuration."""

    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    return jsonify({"config": obj_to_lowercase_key_dict(
        current_app.config,
        exclusions=current_app.config["CONFIG_SECRETS_TO_OBFUSCATE"])})


@bp.route("/versions", methods=["GET"])
@bp.response(200, VersionSchema)
def server_versions():
    """Return the JSON-serialized server component versions.

    This does not require authorization."""

    return jsonify({"versions": versions_to_dict()})
