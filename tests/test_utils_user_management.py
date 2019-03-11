"""Test dtool lookup server user management helper functions."""

from . import tmp_app  # NOQA


def test_user_management_helper_functions(tmp_app):  # NOQA

    from dtool_lookup_server.utils import (
        register_user,
        get_user_info,
    )


    admin_username = "magic.mirror"
    user_id = register_user(admin_username, is_admin=True)
    assert type(user_id) is int

    user_info = get_user_info(admin_username)
    expected_content = {
        "username": admin_username,
        "is_admin": True,
        "base_uris": []
    }
    assert user_info == expected_content

    data_champion_username = "snow-white"
    register_user(data_champion_username)
    user_info = get_user_info(data_champion_username)
    expected_content = {
        "username": data_champion_username,
        "is_admin": False,
        "base_uris": []
    }
    assert user_info == expected_content
