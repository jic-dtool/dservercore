"""Test command line utilities."""

import json
import dservercore

from operator import itemgetter


def test_cli_register_user(tmp_cli_runner):  # NOQA
    from dservercore.utils import user_exists, get_user_obj

    assert not user_exists("admin")

    from dservercore.cli import register_user

    result = tmp_cli_runner.invoke(register_user, ["--is_admin", "admin"])
    assert result.exit_code == 0

    new_user = get_user_obj("admin")
    expected_content = {
        "username": "admin",
        "is_admin": True,
        "search_permissions_on_base_uris": [],
        "register_permissions_on_base_uris": []
    }
    assert new_user.as_dict() == expected_content

    tmp_cli_runner.invoke(register_user, ["dopey"])
    new_user = get_user_obj("dopey")
    expected_content = {
        "username": "dopey",
        "is_admin": False,
        "search_permissions_on_base_uris": [],
        "register_permissions_on_base_uris": []
    }
    assert new_user.as_dict() == expected_content

    result = tmp_cli_runner.invoke(register_user, ["dopey"])
    assert result.exit_code != 0
    assert "User 'dopey' already registered" in result.output


def test_cli_list_users(tmp_cli_runner):  # NOQA
    from dservercore.utils import register_users
    from dservercore.cli import list_users

    register_users([
        {"username": "admin", "is_admin": True},
        {"username": "grumpy"}
    ])

    result = tmp_cli_runner.invoke(list_users, [])
    assert result.exit_code == 0

    expected_content = [
        {
            "username": "admin",
            "is_admin": True,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
        {
            "username": "grumpy",
            "is_admin": False,
            "search_permissions_on_base_uris": [],
            "register_permissions_on_base_uris": []
        },
    ]
    assert json.loads(result.output) == expected_content


def test_cli_register_base_uri(tmp_cli_runner):  # NOQA
    from dservercore.utils import get_base_uri_obj, base_uri_exists

    b_uri = "s3://snow-white"
    assert not base_uri_exists(b_uri)

    from dservercore.cli import add_base_uri

    result = tmp_cli_runner.invoke(add_base_uri, [b_uri])
    assert result.exit_code == 0

    new_base_uri = get_base_uri_obj(b_uri)
    expected_content = {
        "base_uri": b_uri,
        "users_with_search_permissions": [],
        "users_with_register_permissions": []
    }
    assert new_base_uri.as_dict() == expected_content


def test_cli_list_base_uri(tmp_cli_runner):  # NOQA
    from dservercore.utils import register_base_uri

    base_uris = ["s3://snow-white", "s3://mr-men"]
    for uri in base_uris:
        register_base_uri(uri)

    from dservercore.cli import list_base_uris

    result = tmp_cli_runner.invoke(list_base_uris, [])
    assert result.exit_code == 0

    expected_content = sorted([
        {
            "base_uri": uri,
            "users_with_search_permissions": [],
            "users_with_register_permissions": []
        } for uri in base_uris
    ], key=itemgetter("base_uri"))

    actual = sorted(json.loads(result.output), key=itemgetter("base_uri"))
    assert actual == expected_content


def test_cli_give_search_permission(tmp_cli_runner):  # NOQA

    from dservercore.utils import (
        get_base_uri_obj,
        register_users,
        register_base_uri,
    )

    username1 = "sleepy"
    username2 = "dopey"
    base_uri_str = "s3://snow-white"
    register_users([{"username": username1}, {"username": username2}])
    register_base_uri(base_uri_str)

    from dservercore.cli import give_search_permission

    result = tmp_cli_runner.invoke(
        give_search_permission,
        [username1, base_uri_str])
    assert result.exit_code == 0

    base_uri = get_base_uri_obj(base_uri_str)
    expected_content = {
        "base_uri": base_uri_str,
        "users_with_search_permissions": [username1],
        "users_with_register_permissions": []
    }
    assert base_uri.as_dict() == expected_content

    result = tmp_cli_runner.invoke(
        give_search_permission,
        [username2, base_uri_str])
    assert result.exit_code == 0

    base_uri = get_base_uri_obj(base_uri_str)
    expected_content = {
        "base_uri": base_uri_str,
        "users_with_search_permissions": [username1, username2],
        "users_with_register_permissions": []
    }
    assert base_uri.as_dict() == expected_content

    result = tmp_cli_runner.invoke(
        give_search_permission,
        [username2, base_uri_str])
    assert result.exit_code != 0
    assert "User '{}' already has search permissions".format(username2) in result.output  # NOQA

    result = tmp_cli_runner.invoke(
        give_search_permission,
        ["dopey", "s3://no-uri"])
    assert result.exit_code != 0
    assert "Base URI 's3://no-uri' not registered" in result.output

    result = tmp_cli_runner.invoke(
        give_search_permission,
        ["noone", base_uri_str])
    assert result.exit_code != 0
    assert "User 'noone' not registered" in result.output


def test_cli_give_register_permission(tmp_cli_runner):  # NOQA

    from dservercore.utils import (
        get_base_uri_obj,
        register_users,
        register_base_uri,
    )

    username1 = "sleepy"
    username2 = "dopey"
    base_uri_str = "s3://snow-white"
    register_users([{"username": username1}, {"username": username2}])
    register_base_uri(base_uri_str)

    from dservercore.cli import give_register_permission

    result = tmp_cli_runner.invoke(
        give_register_permission,
        [username1, base_uri_str])
    assert result.exit_code == 0

    base_uri = get_base_uri_obj(base_uri_str)
    expected_content = {
        "base_uri": base_uri_str,
        "users_with_search_permissions": [],
        "users_with_register_permissions": [username1]
    }
    assert base_uri.as_dict() == expected_content

    result = tmp_cli_runner.invoke(
        give_register_permission,
        [username2, base_uri_str])
    assert result.exit_code == 0

    base_uri = get_base_uri_obj(base_uri_str)
    expected_content = {
        "base_uri": base_uri_str,
        "users_with_search_permissions": [],
        "users_with_register_permissions": [username1, username2]
    }
    assert base_uri.as_dict() == expected_content

    result = tmp_cli_runner.invoke(
        give_register_permission,
        [username2, base_uri_str])
    assert result.exit_code != 0
    assert "User '{}' already has register permissions".format(username2) in result.output  # NOQA

    result = tmp_cli_runner.invoke(
        give_register_permission,
        ["dopey", "s3://no-uri"])
    assert result.exit_code != 0
    assert "Base URI 's3://no-uri' not registered" in result.output

    result = tmp_cli_runner.invoke(
        give_register_permission,
        ["noone", base_uri_str])
    assert result.exit_code != 0
    assert "User 'noone' not registered" in result.output


def test_cli_config_versions(tmp_cli_runner):  # NOQA
    from dservercore.cli import config_versions

    result = tmp_cli_runner.invoke(config_versions, [])
    assert result.exit_code == 0

    response = json.loads(result.output)

    expected_content = {
        'dservercore': dservercore.__version__,
    }

    for k, v in expected_content.items():
        assert k in response
        assert response[k] == v