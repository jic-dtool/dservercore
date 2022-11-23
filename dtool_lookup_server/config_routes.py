import json
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
from dtool_lookup_server.utils import config_to_dict, versions_to_dict


bp = Blueprint("config", __name__, url_prefix="/config")



def serializable(obj):
    try:
        json.dumps(obj)
    except TypeError:
        return str(obj)
    else:
        return obj


def to_dict(obj):
    """Convert configuration into dict."""
    exclusions = [
        "JWT_PRIVATE_KEY",
    ]  # config keys to exclude
    d = dict()
    for k, v in obj.items():
        # select only capitalized fields
        if k.upper() == k and k not in exclusions:
            d[k.lower()] = serializable(v)
    print(d)
    return d



@bp.route("/info", methods=["GET"])
@jwt_required()
def server_config():
    """Return the JSON-serialized server configuration."""

    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    config = config_to_dict()

    return jsonify(config)


@bp.route("/flat", methods=["GET"])
@jwt_required()
def server_config_flat():
    """Return the JSON-serialized Flask app configuration."""

    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    return jsonify(to_dict(current_app.config))


@bp.route("/versions", methods=["GET"])
def server_versions():
    """Return the JSON-serialized server component versions.

    This does not require authorization."""

    return jsonify(versions_to_dict())
