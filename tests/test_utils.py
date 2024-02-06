"""Test app instance-independent utility functions."""

from dserver import __version__

from dserver.utils import (
    versions_to_dict
)


def test_versions_to_dict():
    versions_dict = versions_to_dict()
    assert 'dserver' in versions_dict
    assert versions_dict['dserver'] == __version__