"""Test the /admin/base_uri blueprint routes."""

import json
import pprint

from . import tmp_app_with_users, tmp_app_with_data  # NOQA

from . import (
    snowwhite_token,
    grumpy_token,
    noone_token,
)


def test_base_uri_regsiter_route(tmp_app_with_users):  # NOQA

    from dtool_lookup_server.utils import base_uri_exists

    base_uri = "s3://snow-white-again"
    assert not base_uri_exists(base_uri)

    data = {"base_uri": base_uri}
    pprint.pprint(data)
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.post(
        "/admin/base_uri/register",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json"
    )
    pprint.pprint(r)
    assert r.status_code == 201
    assert base_uri_exists(base_uri)

    # Ensure idempotent.
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.post(
        "/admin/base_uri/register",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json"
    )
    assert r.status_code == 201
    assert base_uri_exists(base_uri)

    # Only admins allowed. However, don't give away that URL exists to
    # non-admins.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users.post(
        "/admin/base_uri/register",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json"
    )
    assert r.status_code == 404

    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users.post(
        "/admin/base_uri/register",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json"
    )
    assert r.status_code == 404


def test_base_uri_list_route(tmp_app_with_data):  # NOQA

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_data.get(
        "/admin/base_uri/list",
        headers=headers,
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 2

    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data.get(
        "/admin/base_uri/list",
        headers=headers,
    )
    assert r.status_code == 404

    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_data.get(
        "/admin/base_uri/list",
        headers=headers,
    )
    assert r.status_code == 404
