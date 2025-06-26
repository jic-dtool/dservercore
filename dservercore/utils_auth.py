"""Auth utility functions."""

from functools import wraps

from dservercore.sql_models import (
    User,
    BaseURI,
)

from flask import current_app

from flask_jwt_extended import jwt_required as flask_jwt_required
from flask_jwt_extended import get_jwt_identity as flask_get_jwt_identity


def jwt_required(*jwt_required_args, **jwt_required_kwargs):
    """Mark route for requiring JWT authorisation, unless JWT authorisation disabled."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if current_app.config.get("DISABLE_JWT_AUTHORISATION"):
                return fn(*args, **kwargs)
            else:
                return flask_jwt_required(*jwt_required_args, **jwt_required_kwargs)(fn)(*args, **kwargs)
        return decorator
    return wrapper


def get_jwt_identity():
    """Return JWT identity or 'testuser' if JWT authorisation disabled."""
    if current_app.config.get("DISABLE_JWT_AUTHORISATION"):
        return current_app.config.get("DEFAULT_USER")
    else:
        return flask_get_jwt_identity()


def _get_user_obj(username):
    return User.query.filter_by(username=username).first()


def _get_base_uri_obj(base_uri):
    return BaseURI.query.filter_by(base_uri=base_uri).first()


def user_exists(username):
    """Return True if the user exists."""
    user = _get_user_obj(username)
    if user is None:
        return False
    return True


def has_admin_rights(username):
    """Return True if user has admin rights."""
    user = _get_user_obj(username)
    if user is None:
        return False
    return user.is_admin


def may_search(username, base_uri):
    """Return True if user has privileges to search the base URI."""
    user = _get_user_obj(username)
    if user is None:
        return False
    base_uri = _get_base_uri_obj(base_uri)
    if base_uri is None:
        return False
    return base_uri in user.search_base_uris


def may_access(username, uri):
    """Return True if user has privileges to access the dataset URI."""
    base_uri = uri.rsplit("/", 1)[0]
    return may_search(username, base_uri)


def may_register(username, base_uri):
    """Return True if user has privileges to register on the base URI."""
    user = _get_user_obj(username)
    if user is None:
        return False
    base_uri = _get_base_uri_obj(base_uri)
    if base_uri is None:
        return False
    return base_uri in user.register_base_uris


def list_search_base_uris(username):
    """Return list of base URIs the user may search."""
    user = _get_user_obj(username)
    if user is None:
        return []
    return [bu.base_uri for bu in user.search_base_uris]


def list_register_base_uris(username):
    """Return list of base URIs the user may regiester datasets to."""
    user = _get_user_obj(username)
    if user is None:
        return []
    return [bu.base_uri for bu in user.register_base_uris]
