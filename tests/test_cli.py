"""Test command line utilities."""

from . import tmp_cli_runner  # NOQA


def test_search_for_datasets_route(tmp_cli_runner):  # NOQA
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
