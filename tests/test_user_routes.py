"""Test the /user blueprint routes."""

import json

from . import tmp_app_with_users  # NOQA

from . import (
    snowwhite_token,
    grumpy_token,
    noone_token,
)


def test_list_user_route(tmp_app_with_users):  # NOQA

    # Snow-white admin retrieve's her own info.
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.get(
        "/user/info/snow-white",
        headers=headers,
    )
    assert r.status_code == 200

    expected_content = {
        u"username": u"snow-white",
        u"is_admin": True,
        u"search_permissions_on_base_uris": [],
        u"register_permissions_on_base_uris": []
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # Grumpy non-admin retrieve's his own info.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users.get(
        "/user/info/grumpy",
        headers=headers,
    )
    assert r.status_code == 200

    base_uri = "s3://snow-white"
    expected_content = {
        u"username": u"grumpy",
        u"is_admin": False,
        u"search_permissions_on_base_uris": [base_uri],
        u"register_permissions_on_base_uris": [base_uri]
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # Snow-white admin retrieve Grumpy's info.
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.get(
        "/user/info/grumpy",
        headers=headers,
    )
    assert r.status_code == 200

    base_uri = "s3://snow-white"
    expected_content = {
        u"username": u"grumpy",
        u"is_admin": False,
        u"search_permissions_on_base_uris": [base_uri],
        u"register_permissions_on_base_uris": [base_uri]
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # Noone tries to retrieve Grumpy's info. 404.
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users.get(
        "/user/info/grumpy",
        headers=headers,
    )
    assert r.status_code == 404

    # Grumpy tries to retrieve Snow White's info. 404.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users.get(
        "/user/info/snow-white",
        headers=headers,
    )
    assert r.status_code == 404
