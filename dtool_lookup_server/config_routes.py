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

from dtool_lookup_server.schemas import ConfigSchema

from dtool_lookup_server.utils import config_to_dict


bp = Blueprint("config", __name__, url_prefix="/config")


@bp.route("/info", methods=["GET"])
@bp.response(200, ConfigSchema)
@jwt_required()
def server_config():
    """Return the JSON-serialized server configuration."""

    # NOTE: dummy, no authentication implemented here so far.
    username = get_jwt_identity()

    try:
        config = config_to_dict(username)
    except AuthenticationError:
        abort(401)
    return jsonify(config)
