"""Test dservercore URI management helper functions."""


def test_uri_management_helper_functions(tmp_app_client):  # NOQA

    from dservercore.utils import (
        register_base_uri,
        list_base_uris,
    )

    base_uri = "s3://snow-white"
    register_base_uri(base_uri)

    expected_content = [{
        "base_uri": base_uri,
        "users_with_search_permissions": [],
        "users_with_register_permissions": []
    }]
    assert list_base_uris() == expected_content
