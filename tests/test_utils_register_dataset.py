"""Test the dtool_lookup_server.utils.register_dataset helper function."""

import pytest

from . import tmp_app  # NOQA


def test_register_dataset(tmp_app):   # NOQA
    from dtool_lookup_server import ValidationError
    from dtool_lookup_server.utils import (
        register_users,
        register_base_uri,
        update_permissions,
        register_dataset,
        get_admin_metadata_from_uri,
        get_readme_from_uri,
    )

    register_users([
        dict(username="grumpy"),
        dict(username="sleepy"),
    ])

    base_uri = "s3://snow-white"
    register_base_uri(base_uri)

    permissions = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy"],
        "users_with_register_permissions": ["grumpy"],
    }
    update_permissions(permissions)

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "type": "dataset",
        "readme": {"description": "test dataset"},
        "creator_username": "olssont",
    }

    register_dataset(dataset_info)

    expected_content = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
    }
    assert get_admin_metadata_from_uri(uri) == expected_content
    assert get_readme_from_uri(uri) == dataset_info["readme"]

    with pytest.raises(ValidationError):
        register_dataset({"name": "not-all-required-metadata"})
