"""Test the dataset operations on data held in the SQL tables."""

import pytest


def test_sql_dataset_helper_functions(tmp_app_client):  # NOQA

    from dservercore import UnknownBaseURIError
    from dservercore.utils import (
        register_base_uri,
        register_dataset_admin_metadata,
        get_admin_metadata_from_uri,
        list_admin_metadata_in_base_uri,
    )

    base_uri = "s3://snow-white"
    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    admin_metadata = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536236399.19497,
        "number_of_items": 47,
        "size_in_bytes": 5741810,
    }

    # BaseURI not registered yet.
    with pytest.raises(UnknownBaseURIError):
        register_dataset_admin_metadata(admin_metadata)

    register_base_uri(base_uri)

    register_dataset_admin_metadata(admin_metadata)
    assert get_admin_metadata_from_uri(uri) == admin_metadata

    expected_content = [admin_metadata]
    assert list_admin_metadata_in_base_uri(base_uri) == expected_content
