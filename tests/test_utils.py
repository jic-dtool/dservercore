
# from . import tmp_app_with_users  # NOQA
from dtool_lookup_server import __version__

from dtool_lookup_server.utils import (
    config_to_dict,
    versions_to_dict
)


def test_versions_to_dict():
    versions_dict = versions_to_dict()
    assert 'dtool_lookup_server' in versions_dict
    assert versions_dict['dtool_lookup_server'] == __version__