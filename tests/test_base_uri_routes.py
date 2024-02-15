"""Test the /base-uris blueprint routes."""

import json

from dserver.utils import uri_to_url_suffix
from dserver.utils import base_uri_exists


def test_get_base_uri_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA

    base_uri = "s3://snow-white"
    uri_suffix = uri_to_url_suffix(base_uri)

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
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

    # Unregistered user should see 401.
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 401

    # Non-admin user should see 403.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 403


def test_base_uri_register_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA

    base_uri = "s3://snow-white-again"
    assert not base_uri_exists(base_uri)

    uri_suffix = uri_to_url_suffix(base_uri)

    # test without specifying permissions
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.post(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 201
    assert base_uri_exists(base_uri)

    # Ensure idempotency, but distinction in success code
    r = tmp_app_with_users_client.post(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 200
    assert base_uri_exists(base_uri)

    # check empty default permissions
    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 200

    expected_content = {
        "base_uri": base_uri,
        "users_with_search_permissions": [],
        "users_with_register_permissions": []
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # Only admins allowed.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.post(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 403

    # Unregistered users should see 401
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.post(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 401

    # check with non-default permissions
    #
    base_uri = "s3://other-base-uri"
    assert not base_uri_exists(base_uri)

    uri_suffix = uri_to_url_suffix(base_uri)

    post_content = {
        "users_with_search_permissions": ["grumpy", "sleepy"],
        "users_with_register_permissions": ["grumpy"]
    }

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.post(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        json=post_content,
        content_type="application/json"
    )
    assert r.status_code == 201
    assert base_uri_exists(base_uri)

    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
        headers=headers
    )
    assert r.status_code == 200

    expected_content = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy"],
        "users_with_register_permissions": ["grumpy"]
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # ensure idempotency on submitting equivalent permissions
    r = tmp_app_with_users_client.post(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        json=post_content,
        content_type="application/json"
    )
    assert r.status_code == 200
    assert base_uri_exists(base_uri)

    # check empty default permissions
    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 200

    assert json.loads(r.data.decode("utf-8")) == expected_content

    # ensure non-idempotency on extended permissions
    post_content = {
        "users_with_search_permissions": ["sleepy", "snow-white"],
        "users_with_register_permissions": ["grumpy"]
    }

    r = tmp_app_with_users_client.post(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        json=post_content,
        content_type="application/json"
    )
    assert r.status_code == 200
    assert base_uri_exists(base_uri)

    # check empty default permissions
    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 200

    expected_content = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy", "snow-white"],
        "users_with_register_permissions": ["grumpy"]
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content


def test_put_base_uri_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA
    """Put request should reset existing permissions."""

    put_content = {
        "users_with_search_permissions": ["snow-white"],
        "users_with_register_permissions": []
    }

    headers = dict(Authorization="Bearer " + snowwhite_token)

    # test behavior on not-yet-existing base URI

    base_uri = "s3://new-base-uri"
    uri_suffix = uri_to_url_suffix(base_uri)

    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 404

    r = tmp_app_with_users_client.put(
        f"/base-uris/{uri_suffix}",
        json=put_content,
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 201  # created

    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 200  # updated

    expected_content = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["snow-white"],
        "users_with_register_permissions": []
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # test behavior on existing base URI

    base_uri = "s3://snow-white"
    uri_suffix = uri_to_url_suffix(base_uri)

    r = tmp_app_with_users_client.put(
        f"/base-uris/{uri_suffix}",
        json=put_content,
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 200

    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 200

    expected_content = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["snow-white"],
        "users_with_register_permissions": []
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # Unregistered user should see 401.
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.put(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 401

    # Non-admin user should see 403.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.put(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 403


def test_patch_base_uri_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA
    """Patch request should append to existing permissions."""

    base_uri = "s3://non-existing-base-uri"
    uri_suffix = uri_to_url_suffix(base_uri)

    headers = dict(Authorization="Bearer " + snowwhite_token)

    r = tmp_app_with_users_client.patch(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 404

    base_uri = "s3://snow-white"
    uri_suffix = uri_to_url_suffix(base_uri)

    patch_content = {
        "users_with_search_permissions": ["snow-white"],
        "users_with_register_permissions": []
    }

    r = tmp_app_with_users_client.patch(
        f"/base-uris/{uri_suffix}",
        json=patch_content,
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 200

    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        content_type="application/json"
    )
    assert r.status_code == 200

    expected_content = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy","snow-white"],
        "users_with_register_permissions": ["grumpy"]
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # ensure idempotency on repeated permissions
    r = tmp_app_with_users_client.patch(
        f"/base-uris/{uri_suffix}",
        headers=headers,
        json=patch_content,
        content_type="application/json"
    )
    assert r.status_code == 200

    r = tmp_app_with_users_client.get(
        f"/base-uris/{uri_suffix}",
        headers=headers
    )
    assert r.status_code == 200

    expected_content = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy", "snow-white"],
        "users_with_register_permissions": ["grumpy"]
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # Unregistered user should see 401.
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.patch(
        f"/base-uris/{uri_suffix}",
        headers=headers
    )
    assert r.status_code == 401

    # Non-admin user should see 403.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.patch(
        f"/base-uris/{uri_suffix}",
        headers=headers
    )
    assert r.status_code == 403


def test_delete_base_uri_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA

    base_uri = "s3://snow-white"
    uri_suffix = uri_to_url_suffix(base_uri)

    assert base_uri_exists(base_uri)

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.delete(
        f"/base-uris/{uri_suffix}",
        headers=headers
    )
    assert r.status_code == 200
    assert not base_uri_exists(base_uri)

    # assert idempotency
    r = tmp_app_with_users_client.delete(
        f"/base-uris/{uri_suffix}",
        headers=headers
    )
    assert r.status_code == 200
    assert not base_uri_exists(base_uri)

    # Unregistered user should see 401.
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.delete(
        f"/base-uris/{uri_suffix}",
        headers=headers
    )
    assert r.status_code == 401

    # Non-admin user should see 403.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.delete(
        f"/base-uris/{uri_suffix}",
        headers=headers
    )
    assert r.status_code == 403


def test_base_uri_list_route(
        tmp_app_with_data_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_data_client.get(
        "/base-uris",
        headers=headers,
    )
    assert r.status_code == 200

    assert len(json.loads(r.data.decode("utf-8"))) == 2
    expected_content = [
        {'base_uri': 's3://snow-white'},
        {'base_uri': 's3://mr-men'}
    ]
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # add one more base uri
    base_uri = "s3://snow-white-again"
    assert not base_uri_exists(base_uri)

    uri_suffix = uri_to_url_suffix(base_uri)

    # test without specifying permissions
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_data_client.post(
        f"/base-uris/{uri_suffix}",
        headers=headers
    )
    assert r.status_code == 201
    assert base_uri_exists(base_uri)

    # test ascending sorting by id
    r = tmp_app_with_data_client.get(
        "/base-uris",
        query_string={"sort": "+id"},
        headers=headers
    )
    assert r.status_code == 200
    expected_content = [
        {'base_uri': 's3://snow-white'},
        {'base_uri': 's3://mr-men'},
        {'base_uri': 's3://snow-white-again'}
    ]
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # test descending sorting by id
    r = tmp_app_with_data_client.get(
        "/base-uris",
        query_string={"sort": "-id"},
        headers=headers
    )
    assert r.status_code == 200
    expected_content = [
        {'base_uri': 's3://snow-white-again'},
        {'base_uri': 's3://mr-men'},
        {'base_uri': 's3://snow-white'}
    ]
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # test ascending sorting by alphabet
    r = tmp_app_with_data_client.get(
        "/base-uris",
        query_string={"sort": "+base_uri"},
        headers=headers
    )
    assert r.status_code == 200
    expected_content = [
        {'base_uri': 's3://mr-men'},
        {'base_uri': 's3://snow-white'},
        {'base_uri': 's3://snow-white-again'}
    ]
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # test descending sorting by alphabet
    r = tmp_app_with_data_client.get(
        "/base-uris",
        query_string={"sort": "-base_uri"},
        headers=headers
    )
    assert r.status_code == 200
    expected_content = [
        {'base_uri': 's3://snow-white-again'},
        {'base_uri': 's3://snow-white'},
        {'base_uri': 's3://mr-men'},
    ]
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # non-authorized users should get 401
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data_client.get(
        "/base-uris",
        headers=headers,
    )
    assert r.status_code == 403

    # unregistered users should get 401
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_data_client.get(
        "/base-uris",
        headers=headers,
    )
    assert r.status_code == 401
