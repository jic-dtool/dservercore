"""Test the dataset operations on data held in the SQL tables."""

from . import tmp_app  # NOQA


def test_sql_dataset_helper_functions(tmp_app):  # NOQA

    from dtool_lookup_server.utils import (
        register_base_uri,
        register_dataset_admin_metadata,
        get_admin_metadata_from_uri,
        list_admin_metadata_in_base_uri,
    )

    base_uri = "s3://snow-white"
    register_base_uri(base_uri)

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    admin_metadata = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri
    }

    register_dataset_admin_metadata(admin_metadata)
    assert get_admin_metadata_from_uri(uri) == admin_metadata

    expected_content = [admin_metadata]
    assert list_admin_metadata_in_base_uri(base_uri) == expected_content
