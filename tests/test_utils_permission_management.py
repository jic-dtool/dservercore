"""Test dservercore permission management helper functions."""


def test_user_management_helper_functions(tmp_app_client):  # NOQA

    from dservercore.utils import (
        register_users,
        register_base_uri,
        list_users,
        list_base_uris,
        register_permissions,
        get_permission_info,
    )

    base_uri = "s3://snow-white"

    usernames = ["snow-white", "dopey", "sleepy"]
    users = [{"username": u} for u in usernames]

    permissions = {
        "base_uri": base_uri,
        "users_with_search_permissions": usernames,
        "users_with_register_permissions": [usernames[0]],
    }

    register_base_uri(base_uri)
    register_users(users)
    register_permissions(base_uri, permissions)

    assert get_permission_info(base_uri) == permissions

    expected_content = [
        {
            "username": "snow-white",
            "is_admin": False,
            "search_permissions_on_base_uris": ["s3://snow-white"],
            "register_permissions_on_base_uris": ["s3://snow-white"]
        },
        {
            "username": "dopey",
            "is_admin": False,
            "search_permissions_on_base_uris": ["s3://snow-white"],
            "register_permissions_on_base_uris": []
        },
        {
            "username": "sleepy",
            "is_admin": False,
            "search_permissions_on_base_uris": ["s3://snow-white"],
            "register_permissions_on_base_uris": []
        }
    ]
    assert list_users() == expected_content

    expected_content = [{
        "base_uri": base_uri,
        "users_with_search_permissions": ["snow-white", "dopey", "sleepy"],
        "users_with_register_permissions": ["snow-white"]
    }]
    assert list_base_uris() == expected_content

    # Wipe the permissions again.
    permissions = {
        "base_uri": base_uri,
        "users_with_search_permissions": [],
        "users_with_register_permissions": [],
    }
    register_permissions(base_uri, permissions)
    assert get_permission_info(base_uri) == permissions

    expected_content = [
        {
            "username": "snow-white",
            "is_admin": False,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
        {
            "username": "dopey",
            "is_admin": False,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
        {
            "username": "sleepy",
            "is_admin": False,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        }
    ]
    assert list_users() == expected_content

    expected_content = [{
        "base_uri": base_uri,
        "users_with_search_permissions": [],
        "users_with_register_permissions": []
    }]
    assert list_base_uris() == expected_content
