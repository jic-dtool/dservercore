"""Routes for Base URI management"""
from flask import (
    abort,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from flask_smorest.pagination import PaginationParameters

from dserver.blueprint import Blueprint
from dserver.sort import SortParameters, ASCENDING, DESCENDING
from dserver.sql_models import BaseURISchema, BaseURI
import dserver.utils_auth
from dserver.utils import (
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
    """List all base_uris.

    The user needs to be admin.
    """
    identity = get_jwt_identity()

    if not dserver.utils_auth.user_exists(identity):
        abort(401)

    if not dserver.utils_auth.has_admin_rights(identity):
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
@bp.response(200, BaseURISchema)
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def base_uri_get(base_uri):
    """Return base URI information.

    The user needs to be admin.
    """
    identity = get_jwt_identity()

    if not dserver.utils_auth.user_exists(identity):
        abort(401)

    if not dserver.utils_auth.has_admin_rights(identity):
        abort(403)

    base_uri = url_suffix_to_uri(base_uri)

    if not base_uri_exists(base_uri):
        abort(404)

    base_uri_data = get_permission_info(base_uri)
    return base_uri_data


@bp.route("/<path:base_uri>", methods=["PUT"])
@bp.arguments(BaseURISchema)
@bp.response(200)
@bp.alt_response(201, description="Created")
@bp.alt_response(401, description="Not registered")
@bp.alt_response(403, description="No permissions")
@jwt_required()
def base_uri_put(permissions : BaseURISchema, base_uri):
    """Update a user in the dtool lookup server by replacing entry.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dserver.utils_auth.user_exists(identity):
        abort(401)

    if not dserver.utils_auth.has_admin_rights(identity):
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
    """Delete a user from the dtool lookup server.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dserver.utils_auth.user_exists(identity):
        abort(401)

    if not dserver.utils_auth.has_admin_rights(identity):
        abort(403)

    base_uri = url_suffix_to_uri(base_uri)

    delete_base_uri(base_uri)

    return "", 200