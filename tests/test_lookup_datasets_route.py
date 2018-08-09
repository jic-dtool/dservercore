"""Test the /lookup_datasets/<uuid> route."""

import json

from . import tmp_app  # NOQA


def test_lookup_datasets_route(tmp_app):  # NOQA

    # Register a dataset to look up.
    from app.utils import register_dataset

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    data = {
        "uuid": uuid,
        "type": "dataset",
        "uri": "file:///tmp/a_dataset"
    }

    collection = tmp_app.application.config["mongo_collection"]
    register_dataset(collection, data)

    lookup_url = "/lookup_datasets/{}".format(uuid)
    r = tmp_app.get(lookup_url)
    assert [data] == json.loads(r.data)
