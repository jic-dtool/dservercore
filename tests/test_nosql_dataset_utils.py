"""Test the dataset operations on data held in NoSQL database."""

import pytest

from . import tmp_app  # NOQA


def test_get_readme_from_uri(tmp_app):  # NOQA

    from dtool_lookup_server import ValidationError
    from dtool_lookup_server.utils import (
        register_base_uri,
        register_dataset_descriptive_metadata,
        get_readme_from_uri,
    )

    base_uri = "s3://snow-white"

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "type": "dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {
                "e4cc3a7dc281c3d89ed4553293c4b4b110dc9bf3": {
                    "hash": "d89117c9da2cc34586e183017cb14851",
                    "relpath": "U00096.3.rev.1.bt2",
                    "size_in_bytes": 5741810,
                    "utc_timestamp": 1536832115.0
                }
            }
        },
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536236399.19497,
    }

    with pytest.raises(ValidationError):
        register_dataset_descriptive_metadata(dataset_info)

    register_base_uri(base_uri)
    register_dataset_descriptive_metadata(dataset_info)
    assert get_readme_from_uri(uri) == dataset_info["readme"]
