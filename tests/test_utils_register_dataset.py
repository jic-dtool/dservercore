"""Test the dtool_lookup_server.utils.register_dataset helper function."""

import pytest

from . import tmp_app  # NOQA


def test_register_dataset(tmp_app):   # NOQA
    from dtool_lookup_server.utils import (
        register_base_uri,
        register_dataset,
        get_admin_metadata_from_uri,
    )

    base_uri = "s3://snow-white"

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    dataset_metadata = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "type": "dataset",
    }

    register_base_uri(base_uri)
    register_dataset(dataset_metadata)

    expected_content = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
    }
    assert get_admin_metadata_from_uri(uri) == expected_content

    with pytest.raises(ValueError):
        register_dataset({"name": "not-all-required-metadata"})
