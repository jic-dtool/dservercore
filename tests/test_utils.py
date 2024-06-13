"""Test app instance-independent utility functions."""

from dservercore import __version__

from dservercore.utils import (
    versions_to_dict
)


def test_versions_to_dict():
    versions_dict = versions_to_dict()
    assert 'dservercore' in versions_dict
    assert versions_dict['dservercore'] == __version__