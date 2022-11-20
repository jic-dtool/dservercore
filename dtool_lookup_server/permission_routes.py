from flask import abort
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest import Blueprint

import dtool_lookup_server.utils
import dtool_lookup_server.utils_auth
from dtool_lookup_server import (
    AuthenticationError,
    ValidationError
)
from dtool_lookup_server.schemas import URIPermissionSchema
from dtool_lookup_server.sql_models import BaseURISchema

bp = Blueprint("permissions", __name__, url_prefix="/admin/permission")


@bp.route("/info", methods=["POST"])
@bp.arguments(BaseURISchema)
@bp.response(200, URIPermissionSchema)
@jwt_required()
def permission_info(data: BaseURISchema):
    """Get information about the permissions on a base URI.

    The user needs to be admin.
    """
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(username):
        # Non admin should see 404.
        abort(404)

    base_uri = data["base_uri"]

    try:
        return dtool_lookup_server.utils.get_permission_info(base_uri)
    except ValidationError:
        return "", 404


@bp.route("/update_on_base_uri", methods=["POST"])
@bp.arguments(URIPermissionSchema)
@jwt_required()
def update_on_base_uri(permissions: URIPermissionSchema):
    """Update the permissions on a base URI.

    The user needs to be admin.
    """

    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.has_admin_rights(username):
        # Non admin should see 404.
        abort(404)

    # TODO: is it safe to pass this information straight through without
    #       validation?
    dtool_lookup_server.utils.update_permissions(permissions)

    return "", 201
