"""Test the lookup_datasets_by_user_and_uuid helper function."""

from . import tmp_app_with_data  # NOQA


def test_lookup_datasets_by_user_and_uuid(tmp_app_with_data):  # NOQA

    from dtool_lookup_server.utils import lookup_datasets_by_user_and_uuid

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"

    datasets = lookup_datasets_by_user_and_uuid("grumpy", uuid)
    assert len(datasets) == 2

    datasets = lookup_datasets_by_user_and_uuid("sleepy", uuid)
    assert len(datasets) == 0

    assert lookup_datasets_by_user_and_uuid("noone", uuid) is None
