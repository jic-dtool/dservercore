"""Test the /admin/permission blueprint routes."""

import json

from . import tmp_app_with_users  # NOQA

from . import (
    snowwhite_token,
    grumpy_token,
    noone_token,
)


def test_permission_info_route(tmp_app_with_users):  # NOQA

    base_uri = "s3://snow-white"
    data = {"base_uri": base_uri}
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.post(
        "/admin/permission/info",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json"
    )
    assert r.status_code == 200

    expected_content = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy"],
        "users_with_register_permissions": ["grumpy"]
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # Unregistered user should see 404.
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users.post(
        "/admin/permission/info",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json"
    )
    assert r.status_code == 404

    # Non-admin user should see 404.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users.post(
        "/admin/permission/info",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json"
    )
    assert r.status_code == 404


def test_permission_update_all_route(tmp_app_with_users):  # NOQA

    from dtool_lookup_server.utils import get_permission_info
    base_uri = "s3://snow-white"
    expected_content = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy"],
        "users_with_register_permissions": ["grumpy"]
    }
    assert get_permission_info(base_uri) == expected_content

    # New permissions (remove all existing).
    data = {
        "base_uri": base_uri,
        "users_with_search_permissions": [],
        "users_with_register_permissions": []
    }

    # Unregistered user should see 404.
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users.post(
        "/admin/permission/update_on_base_uri",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json"
    )
    assert r.status_code == 404

    # Non-admin user should see 404.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users.post(
        "/admin/permission/update_on_base_uri",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json"
    )
    assert r.status_code == 404

    # Finally change the permission.
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.post(
        "/admin/permission/update_on_base_uri",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json"
    )
    assert r.status_code == 201
    assert get_permission_info(base_uri) == data
