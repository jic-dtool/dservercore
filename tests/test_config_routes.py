"""Test the /config blueprint routes."""

import json
import dservercore


def test_config_info_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.get(
        "/config/info",
        headers=headers,
    )
    assert r.status_code == 200

    # NOTE: If the configuration grows in the future, this text must adapt or
    # will fail otherwise.
    expected_content = {
        'jwt_algorithm': 'RS256',
        'jwt_header_name': 'Authorization',
        'jwt_header_type': 'Bearer',
        'jwt_token_location': 'headers',
        'sqlalchemy_track_modifications': False,
    }

    response = json.loads(r.data.decode("utf-8"))["config"]

    for k, v in expected_content.items():
        assert k in response
        assert v == response[k]


def test_config_info_route_authorization(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token):  # NOQA
    # All users in the system should have access to the /config route.
    # For example "snow-white" and "grumpy"
    for t in (snowwhite_token, grumpy_token):
        headers = dict(Authorization="Bearer " + snowwhite_token)
        r = tmp_app_with_users_client.get(
            "/config/info",
            headers=headers,
        )
        assert r.status_code == 200

    # However a user that is not registered in the system should get 401.
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.get(
        "/config/info",
        headers=headers,
    )
    assert r.status_code == 401


def test_config_versions_route(tmp_app_client):

    r = tmp_app_client.get("/config/versions")
    assert r.status_code == 200

    response = json.loads(r.data.decode("utf-8"))["versions"]

    expected_content = {
        'dservercore': dservercore.__version__,
    }

    for k, v in expected_content.items():
        assert k in response
        assert v == response[k]
