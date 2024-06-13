"""Routes for me (information on currently authenticated user)"""
from flask import (
    abort,
    jsonify,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

import dtool_lookup_server.utils
import dtool_lookup_server.utils_auth

from dtool_lookup_server.blueprint import Blueprint
from dtool_lookup_server.sql_models import UserSchema, UserWithPermissionsSchema
from dtool_lookup_server.schemas import SummarySchema
from dtool_lookup_server.utils import summary_of_datasets_by_user


bp = Blueprint("me", __name__, url_prefix="/me")


@bp.route("", methods=["GET"])
@bp.response(200, UserWithPermissionsSchema)
@bp.alt_response(401, description="Not registered")
@jwt_required()
def me_get():
    """Return information on me (the user currently authenticated)."""
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    return dtool_lookup_server.utils.get_user_info(identity)


@bp.route("/summary", methods=["GET"])
@bp.response(200, SummarySchema)
@bp.alt_response(401, description="Not registered")
@jwt_required()
def me_summary_get():
    """Global summary of the datasets the currently authenticated user has access to."""
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        # Authenticated user does not exist
        abort(401)

    summary = summary_of_datasets_by_user(identity)
    return summary
