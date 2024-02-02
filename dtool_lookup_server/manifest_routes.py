from flask import (
    abort,
    jsonify,
    current_app
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from dtool_lookup_server import UnknownURIError
from dtool_lookup_server.blueprint import Blueprint
import dtool_lookup_server.utils_auth
from dtool_lookup_server.utils import (
    url_suffix_to_uri,
    get_manifest_from_uri_by_user
)

bp = Blueprint("manifests", __name__, url_prefix="/manifests")

@bp.route("/<path:uri>", methods=["GET"])
@jwt_required()
def manifest(uri):
    """Request the dataset manifest."""
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    uri = url_suffix_to_uri(uri)
    if not dtool_lookup_server.utils_auth.may_access(username, uri):
        # Authorization errors should return 400.
        abort(400)

    try:
        manifest_ = get_manifest_from_uri_by_user(username, uri)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(400)

    return jsonify(manifest_)


