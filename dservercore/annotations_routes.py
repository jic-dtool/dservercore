"""Routes for retrieving and modifying dataset annotations by URI."""
from flask import (
    abort,
    jsonify,
    current_app,
    request
)
from dservercore.utils_auth import (
    jwt_required,
    get_jwt_identity,
)

from dservercore import UnknownURIError, AuthorizationError
from dservercore.blueprint import Blueprint
from dservercore.schemas import AnnotationSchema, SingleAnnotationSchema
import dservercore.utils_auth
from dservercore.utils import (
    url_suffix_to_uri,
    get_annotations_from_uri_by_user,
    set_annotations_for_uri_by_user,
    set_annotation_for_uri_by_user,
    delete_annotation_for_uri_by_user
)

bp = Blueprint("annotations", __name__, url_prefix="/annotations")


@bp.route("/<path:uri>", methods=["GET"])
@bp.response(200, AnnotationSchema)
@bp.alt_response(401, description="Unauthorized")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def get_annotations(uri):
    """Request the dataset annotations."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
        abort(401)

    uri = url_suffix_to_uri(uri)

    if not dservercore.utils_auth.may_access(username, uri):
        abort(403)

    try:
        annotations = get_annotations_from_uri_by_user(username, uri)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(404)

    return {"annotations": annotations}


@bp.route("/<path:uri>", methods=["PUT"])
@bp.arguments(AnnotationSchema)
@bp.response(200, AnnotationSchema)
@bp.alt_response(401, description="Unauthorized")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def set_annotations(data, uri):
    """Set all dataset annotations (replaces existing annotations)."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
        abort(401)

    uri = url_suffix_to_uri(uri)

    try:
        annotations = set_annotations_for_uri_by_user(
            username, uri, data.get("annotations", {})
        )
    except AuthorizationError:
        abort(403)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(404)

    return {"annotations": annotations}


@bp.route("/<path:uri>/<annotation_name>", methods=["PUT"])
@bp.arguments(SingleAnnotationSchema)
@bp.response(200, AnnotationSchema)
@bp.alt_response(401, description="Unauthorized")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def set_annotation(data, uri, annotation_name):
    """Set a single annotation (creates or updates)."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
        abort(401)

    uri = url_suffix_to_uri(uri)

    try:
        annotations = set_annotation_for_uri_by_user(
            username, uri, annotation_name, data.get("value")
        )
    except AuthorizationError:
        abort(403)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(404)

    return {"annotations": annotations}


@bp.route("/<path:uri>/<annotation_name>", methods=["DELETE"])
@bp.response(200, AnnotationSchema)
@bp.alt_response(401, description="Unauthorized")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def delete_annotation(uri, annotation_name):
    """Delete a single annotation."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
        abort(401)

    uri = url_suffix_to_uri(uri)

    try:
        annotations = delete_annotation_for_uri_by_user(
            username, uri, annotation_name
        )
    except AuthorizationError:
        abort(403)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(404)

    return {"annotations": annotations}