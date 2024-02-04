from flask import (
    abort,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from flask_smorest.pagination import PaginationParameters

from dtool_lookup_server.blueprint import Blueprint
from dtool_lookup_server.sort import SortParameters, ASCENDING, DESCENDING
from dtool_lookup_server.sql_models import BaseURISchema, BaseURI
from dtool_lookup_server.schemas import UserPermissionsOnBaseURISchema
import dtool_lookup_server.utils_auth
from dtool_lookup_server.utils import (
    base_uri_exists,
    get_permission_info,
    register_base_uri,
    delete_base_uri,
    put_permissions,
    patch_permissions,
    url_suffix_to_uri
)

bp = Blueprint("base_uris", __name__, url_prefix="/base_uris")


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
@bp.sort(sort=["+id"], allowed_sort_fields=["id", "base_uri"])
@bp.paginate()
@bp.response(200, BaseURISchema(many=True))
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@jwt_required()
def base_uri_list(pagination_parameters : PaginationParameters,
                  sort_parameters : SortParameters):
    """List all base_uris.

    The user needs to be admin.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(403)

    order_by_args = []
    for field, order in sort_parameters.order().items():
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
@bp.response(200, UserPermissionsOnBaseURISchema)
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@jwt_required()
def get_base_uri(base_uri):
    """Return base URI information.

    The user needs to be admin.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(403)

    base_uri = url_suffix_to_uri(base_uri)
    base_uri_data = get_permission_info(base_uri)
    return base_uri_data


@bp.route("/<path:base_uri>", methods=["POST"])
@bp.arguments(UserPermissionsOnBaseURISchema)
@bp.response(201)
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@jwt_required()
def register(permissions: UserPermissionsOnBaseURISchema, base_uri):
    """Register a base URI.

    The user needs to be admin.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(403)

    base_uri = url_suffix_to_uri(base_uri)

    if not base_uri_exists(base_uri):
        register_base_uri(base_uri)

    # post method not idempotent
    patch_permissions(base_uri, permissions)

    return "", 201


@bp.route("/<path:base_uri>", methods=["PUT"])
@bp.arguments(UserPermissionsOnBaseURISchema)
@bp.response(200)
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@jwt_required()
def put_update(permissions : UserPermissionsOnBaseURISchema, base_uri):
    """Update a user in the dtool lookup server by replacing entry.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(403)

    base_uri = url_suffix_to_uri(base_uri)

    if not base_uri_exists(base_uri):
        register_base_uri(base_uri)

    # put method idempotent
    put_permissions(base_uri, permissions)

    return "", 200


@bp.route("/<path:base_uri>", methods=["PATCH"])
@bp.arguments(UserPermissionsOnBaseURISchema)
@bp.response(200)
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@bp.alt_response(404, "Not found")
@jwt_required()
def patch_update(permissions : UserPermissionsOnBaseURISchema, base_uri):
    """Update a user in the dtool lookup server by patching fields.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(403)

    base_uri = url_suffix_to_uri(base_uri)

    # patch only updates existing resources, but does not create
    if not base_uri_exists(base_uri):
        abort(404)

    patch_permissions(base_uri, permissions)

    return "", 200


@bp.route("/<path:base_uri>", methods=["DELETE"])
@bp.response(200)
@bp.alt_response(401, "Not registered")
@bp.alt_response(403, "No permissions")
@jwt_required()
def delete(base_uri):
    """Delete a user from the dtool lookup server.

    The user in the Authorization token needs to be admin.
    """
    identity = get_jwt_identity()

    if not dtool_lookup_server.utils_auth.user_exists(identity):
        abort(401)

    if not dtool_lookup_server.utils_auth.has_admin_rights(identity):
        abort(403)

    base_uri = url_suffix_to_uri(base_uri)

    delete_base_uri(base_uri)

    return "", 200