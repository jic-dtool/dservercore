"""Test that the various dtool-lookup-server modules work together."""

import dtool_lookup_server_core as dls_core


def test_dls_core_version_is_string():
    assert isinstance(dls_core.__version__, str)

def test_auth_integration():
    from dtool_lookup_server_core.plugins import auth_plugin
    assert issubclass(auth_plugin, dls_core.abc.AuthABC)

def test_search_integration():
    from dtool_lookup_server_core.plugins import search_plugin
    assert issubclass(search_plugin, dls_core.abc.SearchABC)
