"""Test dservercore user management helper functions."""


def test_user_management_helper_functions(tmp_app_client):  # NOQA

    from dservercore.utils import (
        register_users,
        get_user_info,
        list_users,
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
        "search_permissions_on_base_uris": [],
        "register_permissions_on_base_uris": []
    }
    assert user_info == expected_content

    user_info = get_user_info(data_champion_username)
    expected_content = {
        "username": data_champion_username,
        "is_admin": False,
        "search_permissions_on_base_uris": [],
        "register_permissions_on_base_uris": []
    }
    assert user_info == expected_content

    user_info = get_user_info(standard_user_username)
    expected_content = {
        "username": standard_user_username,
        "is_admin": False,
        "search_permissions_on_base_uris": [],
        "register_permissions_on_base_uris": []
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
        "search_permissions_on_base_uris": [],
        "register_permissions_on_base_uris": []
    }
    assert user_info == expected_content

    # Test listing users.
    expected_content = [
        {
            "username": admin_username,
            "is_admin": True,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
        {
            "username": data_champion_username,
            "is_admin": False,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
        {
            "username": standard_user_username,
            "is_admin": False,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
        {
            "username": new_username,
            "is_admin": False,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
    ]
    assert list_users() == expected_content

    # Test deleting users.
    from dservercore.utils import delete_users

    users_to_delete = [
        {
            "username": standard_user_username,
            "is_admin": False,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
        {
            "username": new_username,
            "is_admin": False,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
    ]
    delete_users(users_to_delete)

    expected_content = [
        {
            "username": admin_username,
            "is_admin": True,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
        {
            "username": data_champion_username,
            "is_admin": False,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
    ]
    assert list_users() == expected_content

    # Test updating users admin privileges.
    from dservercore.utils import update_users

    users_to_update = [
        {"username": admin_username},  # The is_admin value defaults to False.
        {"username": data_champion_username, "is_admin": True},
        {"username": standard_user_username},  # Not in system so ignored.
    ]
    update_users(users_to_update)

    expected_content = [
        {
            "username": admin_username,
            "is_admin": False,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
        {
            "username": data_champion_username,
            "is_admin": True,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
    ]
    assert list_users() == expected_content
