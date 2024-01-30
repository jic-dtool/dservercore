"""Test the /base_uris blueprint routes."""

import json

from dtool_lookup_server.utils import uri_to_url_suffix


def test_base_uri_register_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA
    from dtool_lookup_server.utils import base_uri_exists

    base_uri = "s3://snow-white-again"
    assert not base_uri_exists(base_uri)

    uri_suffix = uri_to_url_suffix(base_uri)

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.post(
        f"/base_uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 201
    assert base_uri_exists(base_uri)

    # Ensure idempotent.
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.post(
        f"/base_uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 201
    assert base_uri_exists(base_uri)

    # Only admins allowed. However, don't give away that URL exists to
    # non-admins.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.post(
        f"/base_uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 404

    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.post(
        f"/base_uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 404


def test_put_base_uri_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA

    base_uri = "s3://snow-white"
    uri_suffix = uri_to_url_suffix(base_uri)

    put_content = {
        "users_with_search_permissions": ["snowwhite"],
        "users_with_register_permissions": []
    }

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.put(
        f"/base_uris/{uri_suffix}",
        data=put_content,
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 200

    r = tmp_app_with_users_client.get(
        f"/base_uris/{uri_suffix}",
        headers=headers,
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
    r = tmp_app_with_users_client.put(
        f"/base_uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 404

    # Non-admin user should see 404.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.put(
        f"/base_uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 404


def test_get_base_uri_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA

    base_uri = "s3://snow-white"
    uri_suffix = uri_to_url_suffix(base_uri)

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.get(
        f"/base_uris/{uri_suffix}",
        headers=headers,
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
    r = tmp_app_with_users_client.get(
        f"/base_uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 404

    # Non-admin user should see 404.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.get(
        f"/base_uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 404


def test_base_uri_list_route(
        tmp_app_with_data_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_data_client.get(
        "/base_uris",
        headers=headers,
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 2

    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data_client.get(
        "/base_uris",
        headers=headers,
    )
    assert r.status_code == 404

    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_data_client.get(
        "/base_uris",
        headers=headers,
    )
    assert r.status_code == 404
