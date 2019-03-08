"""Test the /register_dataset route."""

import json

from . import tmp_app  # NOQA


def test_register_dataset_route(tmp_app):  # NOQA

    from dtool_lookup_server import mongo
    from dtool_lookup_server.utils import lookup_datasets

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    data = {
        "uuid": uuid,
        "type": "dataset",
        "uri": "file:///tmp/a_dataset"
    }
    r = tmp_app.post(
        "/register_dataset",
        data=json.dumps(data),
        content_type='application/json'
    )

    assert r.status_code == 200

    # Check that the dataset has been added to mongo.
    collection = mongo.db.datasets
    assert [data] == lookup_datasets(collection, uuid)


def test_register_dataset_route_returns_bad_request_when_dataset_info_is_invalid(tmp_app):  # NOQA
    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    data = {
        "uuid": uuid,
        "type": "protodataset",
        "uri": "file:///tmp/a_dataset"
    }

    r = tmp_app.post(
        "/register_dataset",
        data=json.dumps(data),
        content_type='application/json'
    )

    assert r.status_code == 400
