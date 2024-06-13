"""Route for retrieving dataset annotations by URI."""
from flask import (
    abort,
    jsonify,
    current_app
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from dservercore import UnknownURIError
from dservercore.blueprint import Blueprint
from dservercore.schemas import AnnotationSchema
import dservercore.utils_auth
from dservercore.utils import (
    url_suffix_to_uri,
    get_annotations_from_uri_by_user
)

bp = Blueprint("annotations", __name__, url_prefix="/annotations")


@bp.route("/<path:uri>", methods=["GET"])
@bp.response(200, AnnotationSchema)
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(400, description="Unknown URI")
@jwt_required()
def annotations(uri):
    """Request the dataset annotations."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    uri = url_suffix_to_uri(uri)

    if not dservercore.utils_auth.may_access(username, uri):
        # Authorization errors should return 403.
        abort(403)

    try:
        annotations = get_annotations_from_uri_by_user(username, uri)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(404)

    return {"annotations": annotations}