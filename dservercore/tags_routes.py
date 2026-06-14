"""Routes for retrieving and modifying tags of a dataset"""
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
from dservercore.schemas import TagSchema
import dservercore.utils_auth
from dservercore.utils import (
    url_suffix_to_uri,
    get_tags_from_uri_by_user,
    set_tags_for_uri_by_user
)

bp = Blueprint("tags", __name__, url_prefix="/tags")


@bp.route("/<path:uri>", methods=["GET"])
@bp.response(200, TagSchema)
@bp.alt_response(401, description="Unauthorized")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def get_tags(uri):
    """Request the dataset tags."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
        abort(401)

    uri = url_suffix_to_uri(uri)
    if not dservercore.utils_auth.may_access(username, uri):
        abort(403)

    try:
        tags = get_tags_from_uri_by_user(username, uri)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(404)

    return {"tags": tags}


@bp.route("/<path:uri>", methods=["PUT"])
@bp.arguments(TagSchema)
@bp.response(200, TagSchema)
@bp.alt_response(401, description="Unauthorized")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def set_tags(data, uri):
    """Set the dataset tags (replaces all existing tags)."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
        abort(401)

    uri = url_suffix_to_uri(uri)

    try:
        tags = set_tags_for_uri_by_user(username, uri, data.get("tags", []))
    except AuthorizationError:
        abort(403)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(404)

    return {"tags": tags}


@bp.route("/<path:uri>/<tag>", methods=["POST"])
@bp.response(200, TagSchema)
@bp.alt_response(401, description="Unauthorized")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def add_tag(uri, tag):
    """Add a single tag to the dataset."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
        abort(401)

    uri = url_suffix_to_uri(uri)

    try:
        # Get existing tags
        existing_tags = get_tags_from_uri_by_user(username, uri)
        # Add new tag if not already present
        if tag not in existing_tags:
            existing_tags.append(tag)
        # Set updated tags
        tags = set_tags_for_uri_by_user(username, uri, existing_tags)
    except AuthorizationError:
        abort(403)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(404)

    return {"tags": tags}


@bp.route("/<path:uri>/<tag>", methods=["DELETE"])
@bp.response(200, TagSchema)
@bp.alt_response(401, description="Unauthorized")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def delete_tag(uri, tag):
    """Remove a single tag from the dataset."""
    username = get_jwt_identity()
    if not dservercore.utils_auth.user_exists(username):
        abort(401)

    uri = url_suffix_to_uri(uri)

    try:
        # Get existing tags
        existing_tags = get_tags_from_uri_by_user(username, uri)
        # Remove tag if present
        if tag in existing_tags:
            existing_tags.remove(tag)
        # Set updated tags
        tags = set_tags_for_uri_by_user(username, uri, existing_tags)
    except AuthorizationError:
        abort(403)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(404)

    return {"tags": tags}


