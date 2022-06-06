"""Unit tests for the core module."""

import pytest


def test_get_plugin():
    from dtool_lookup_server_core.plugins import get_plugin

    # Should raise RuntimeError if there is more than one plugin available.
    with pytest.raises(RuntimeError):
        get_plugin("setuptools.finalize_distribution_options")

    # Should raise RuntimeError if no plugin exists.
    with pytest.raises(RuntimeError):
        get_plugin("dontexist")