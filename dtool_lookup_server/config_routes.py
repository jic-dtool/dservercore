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

from dtool_lookup_server.utils import config_to_dict


bp = Blueprint("config", __name__, url_prefix="/config")


@bp.route("/info", methods=["GET"])
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
