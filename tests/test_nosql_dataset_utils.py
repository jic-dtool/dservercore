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
    }

    with pytest.raises(ValidationError):
        register_dataset_descriptive_metadata(dataset_info)

    register_base_uri(base_uri)
    register_dataset_descriptive_metadata(dataset_info)
    assert get_readme_from_uri(uri) == dataset_info["readme"]
