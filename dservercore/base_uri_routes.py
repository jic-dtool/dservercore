"""Routes for Base URI management"""
from flask import (
    abort,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from flask_smorest.pagination import PaginationParameters

from dservercore.blueprint import Blueprint
from dservercore.sort import SortParameters, ASCENDING, DESCENDING
from dservercore.sql_models import BaseURISchema, BaseURIWithPermissionsSchema, BaseURI
import dservercore.utils_auth
from dservercore.utils import (
    base_uri_exists,
    get_permission_info,
    register_base_uri,
    delete_base_uri,
    register_permissions,
    url_suffix_to_uri
)

bp = Blueprint("base-uris", __name__, url_prefix="/base-uris")


@bp.route("", methods=["GET"])
@bp.sort(sort=["+base_uri"], allowed_sort_fields=["base_uri"])
@bp.paginate()
@bp.response(200, BaseURISchema(many=True))
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@jwt_required()
def base_uris_get(pagination_parameters : PaginationParameters,
                  sort_parameters : SortParameters):
    """List all base URIs.

    The user needs to be admin.
    """
    identity = get_jwt_identity()

    if not dservercore.utils_auth.user_exists(identity):
        abort(401)

    if not dservercore.utils_auth.has_admin_rights(identity):
        abort(403)

    order_by_args = []
    for field, order in sort_parameters.order.items():
        if not hasattr(BaseURI, field):
            continue
        if order == DESCENDING:
            order_by_args.append(getattr(BaseURI, field).desc())
        else:  # ascending
            order_by_args.append(getattr(BaseURI, field))

    query = BaseURI.query.order_by(*order_by_args).filter_by()
    pagination_parameters.item_count = query.count()
    return query.paginate(
        page=pagination_parameters.page,
        per_page=pagination_parameters.page_size,
        error_out=True
    ).items


# per default, route parameters can contain any character except for a forward
# slash '/' and a period '.'. To include a forward slash in the parameter, you
# can specify a custom converter for the route parameter, e.g. <path:base_uri>
@bp.route("/<path:base_uri>", methods=["GET"])
@bp.response(200, BaseURIWithPermissionsSchema)
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def base_uri_get(base_uri):
    """Return base URI information.

    The user needs to be admin.
    """
    identity = get_jwt_identity()

    if not dservercore.utils_auth.user_exists(identity):
        abort(401)

    if not dservercore.utils_auth.has_admin_rights(identity):
        abort(403)

    base_uri = url_suffix_to_uri(base_uri)

    if not base_uri_exists(base_uri):
        abort(404)

    base_uri_data = get_permission_info(base_uri)
    return base_uri_data


@bp.route("/<path:base_uri>", methods=["PUT"])
@bp.arguments(BaseURIWithPermissionsSchema)
@bp.response(200)
@bp.alt_response(201, description="Created")
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@jwt_required()
def base_uri_put(permissions : BaseURIWithPermissionsSchema, base_uri):
    """Create or update a base URI in dserver by replacing entry.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dservercore.utils_auth.user_exists(identity):
        abort(401)

    if not dservercore.utils_auth.has_admin_rights(identity):
        abort(403)

    base_uri = url_suffix_to_uri(base_uri)

    success_code = 200  # updated
    if not base_uri_exists(base_uri):
        register_base_uri(base_uri)
        success_code = 201  # created

    # put method idempotent
    register_permissions(base_uri, permissions)

    return "", success_code


@bp.route("/<path:base_uri>", methods=["DELETE"])
@bp.response(200)
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@jwt_required()
def base_uri_delete(base_uri):
    """Delete a base URI from dserver.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dservercore.utils_auth.user_exists(identity):
        abort(401)

    if not dservercore.utils_auth.has_admin_rights(identity):
        abort(403)

    base_uri = url_suffix_to_uri(base_uri)

    delete_base_uri(base_uri)

    return "", 200