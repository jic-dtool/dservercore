"""Test the /config blueprint routes."""

import json
import dtool_lookup_server

from . import tmp_app, tmp_app_with_users  # NOQA

from . import (
    snowwhite_token,
    grumpy_token,
    noone_token,
)


def test_config_info_route(tmp_app_with_users):  # NOQA

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.get(
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

    response = json.loads(r.data.decode("utf-8"))

    for k, v in expected_content.items():
        assert k in response
        assert v == response[k]


def test_config_info_route_authorization(tmp_app_with_users):  # NOQA

    # All users in the system should have access to the /config route.
    # For example "snow-white" and "grumpy"
    for t in (snowwhite_token, grumpy_token):
        headers = dict(Authorization="Bearer " + snowwhite_token)
        r = tmp_app_with_users.get(
            "/config/info",
            headers=headers,
        )
        assert r.status_code == 200

    # However a user that is not registered in the system should get 401.
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users.get(
        "/config/info",
        headers=headers,
    )
    assert r.status_code == 401



def test_config_versions_route(tmp_app):

    r = tmp_app.get("/config/versions")
    assert r.status_code == 200

    response = json.loads(r.data.decode("utf-8"))

    expected_content = {
        'dtool_lookup_server': dtool_lookup_server.__version__,
    }

    for k, v in expected_content.items():
        assert k in response
        assert v == response[k]
