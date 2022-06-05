"""Unit tests for the auth module."""

import dtool_lookup_server_auth as dls_auth

def test_non_existing_user_is_not_admin():
    auth = dls_auth.Auth()
    assert not auth.has_admin_rights("dont_exist")
