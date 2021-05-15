"""Test the /admin/user blueprint routes."""

import json

from . import tmp_app_with_users  # NOQA

from . import (
    snowwhite_token,
    grumpy_token,
    noone_token,
)


def test_register_user_route(tmp_app_with_users):  # NOQA

    from dtool_lookup_server.utils import user_exists

    assert not user_exists("evil-witch")
    assert not user_exists("dopey")

    users = [
        {"username": "evil-witch", "is_admin": True},
        {"username": "dopey"}
    ]
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.post(
        "/admin/user/register",
        headers=headers,
        data=json.dumps(users),
        content_type="application/json"
    )
    assert r.status_code == 201
    assert user_exists("evil-witch")
    assert user_exists("dopey")

    # Ensure idempotent.
    r = tmp_app_with_users.post(
        "/admin/user/register",
        headers=headers,
        data=json.dumps(users),
        content_type="application/json"
    )
    assert r.status_code == 201
    assert user_exists("evil-witch")
    assert user_exists("dopey")

    # Only admins allowed. However, don't give away that URL exists to
    # non-admins.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users.post(
        "/admin/user/register",
        headers=headers,
        data=json.dumps(users),
        content_type="application/json"
    )
    assert r.status_code == 404

    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users.post(
        "/admin/user/register",
        headers=headers,
        data=json.dumps(users),
        content_type="application/json"
    )
    assert r.status_code == 404


def test_list_user_route(tmp_app_with_users):  # NOQA

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.get(
        "/admin/user/list",
        headers=headers,
    )
    assert r.status_code == 200

    # Only admins allowed. However, don't give away that URL exists to
    # non-admins.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users.get(
        "/admin/user/list",
        headers=headers
    )
    assert r.status_code == 404

    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users.get(
        "/admin/user/list",
        headers=headers
    )
    assert r.status_code == 404
