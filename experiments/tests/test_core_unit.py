"""Unit tests for the core module."""

import pytest


def test_get_plugin():
    from dtool_lookup_server_core.plugins import get_plugin

    with pytest.raises(RuntimeError):
        get_plugin("setuptools.finalize_distribution_options")

    with pytest.raises(RuntimeError):
        get_plugin("dontexist")