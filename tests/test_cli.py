"""Test command line utilities."""

from . import tmp_cli_runner  # NOQA


def test_cli_register_user(tmp_cli_runner):  # NOQA
    from dtool_lookup_server.utils import _get_user_obj

    assert _get_user_obj("admin") is None

    from dtool_lookup_server.cli import register_user

    result = tmp_cli_runner.invoke(register_user, ["--is_admin", "admin"])
    assert result.exit_code == 0

    new_user = _get_user_obj("admin")
    expected_content = {
        "username": "admin",
        "is_admin": True,
        "search_permissions_on_base_uris": [],
        "register_permissions_on_base_uris": []
    }
    assert new_user.as_dict() == expected_content

    tmp_cli_runner.invoke(register_user, ["dopey"])
    new_user = _get_user_obj("dopey")
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


def test_cli_register_base_uri(tmp_cli_runner):  # NOQA
    from dtool_lookup_server.utils import _get_base_uri_obj

    b_uri = "s3://snow-white"
    assert _get_base_uri_obj(b_uri) is None

    from dtool_lookup_server.cli import add_base_uri

    result = tmp_cli_runner.invoke(add_base_uri, [b_uri])
    assert result.exit_code == 0

    new_base_uri = _get_base_uri_obj(b_uri)
    expected_content = {
        "base_uri": b_uri,
        "users_with_search_permissions": [],
        "users_with_register_permissions": []
    }
    assert new_base_uri.as_dict() == expected_content
