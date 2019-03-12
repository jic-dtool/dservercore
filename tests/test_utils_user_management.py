"""Test dtool lookup server user management helper functions."""

from . import tmp_app  # NOQA


def test_user_management_helper_functions(tmp_app):  # NOQA

    from dtool_lookup_server.utils import (
        register_users,
        get_user_info,
    )

    # Create list of dictionaries of users.
    admin_username = "magic.mirror"
    data_champion_username = "snow-white"
    standard_user_username = "dopey"
    users = [
        {"username": admin_username, "is_admin": True},
        {"username": data_champion_username, "is_admin": False},
        {"username": standard_user_username},
    ]

    # Register the users.
    register_users(users)

    user_info = get_user_info(admin_username)
    expected_content = {
        "username": admin_username,
        "is_admin": True,
        "base_uris": []
    }
    assert user_info == expected_content

    user_info = get_user_info(data_champion_username)
    expected_content = {
        "username": data_champion_username,
        "is_admin": False,
        "base_uris": []
    }
    assert user_info == expected_content

    user_info = get_user_info(standard_user_username)
    expected_content = {
        "username": standard_user_username,
        "is_admin": False,
        "base_uris": []
    }
    assert user_info == expected_content

    # Test non-existing user.
    assert get_user_info("no-one") is None

    # Test registering input with an existing user present.
    new_username = "sleepy"
    users = [{"username": data_champion_username}, {"username": new_username}]
    register_users(users)
    user_info = get_user_info(new_username)
    expected_content = {
        "username": new_username,
        "is_admin": False,
        "base_uris": []
    }
    assert user_info == expected_content
