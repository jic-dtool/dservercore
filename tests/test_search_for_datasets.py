"""Test /search_for_datasets route."""

import json
from operator import itemgetter

from . import tmp_app  # NOQA


def test_search_for_datasets_route(tmp_app):  # NOQA

    from dtool_lookup_server import mongo
    from dtool_lookup_server.utils import (
        _register_dataset_descriptive_metadata,
    )

    # Get the collection out of the tmp_app.
    collection = mongo.db.datasets

    # Use register_dataset_descriptive_metadata to register some datasets.
    datasets_to_register = [
        {
            u"creator_username": u"olssont",
            u"uuid": u"c58038a4-3a54-425e-9087-144d0733387f",
            u"type": "dataset",
            u"name": u"lamda-phage-genome",
            "readme": {"description": "a dataset"},
            u"uri": u"s3://dtool-demo/c58038a4-3a54-425e-9087-144d0733387f",
            u"base_uri": u"s3://dtool-demo",
        },
        {
            u"uuid": u"af6727bf-29c7-43dd-b42f-a5d7ede28337",
            u"creator_username": u"olssont",
            u"type": u"dataset",
            u"name": u"simulated-lambda-phage-reads",
            "readme": {"description": "a dataset"},
            u"uri": u"s3://dtool-demo/af6727bf-29c7-43dd-b42f-a5d7ede28337",
            u"base_uri": u"s3://dtool-demo",
        }
    ]
    for ds_info in datasets_to_register:
        r = _register_dataset_descriptive_metadata(collection, ds_info)
    assert collection.count() == 2

    # Do some search tests.
    query = {}  # Everything.
    r = tmp_app.post(
        "/search_for_datasets",
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert sorted(datasets_to_register, key=itemgetter("uuid")) == sorted(json.loads(r.data), key=itemgetter("uuid"))  # NOQA

    query = {"creator_username": "olssont"}
    r = tmp_app.post(
        "/search_for_datasets",
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert sorted(datasets_to_register, key=itemgetter("uuid")) == sorted(json.loads(r.data), key=itemgetter("uuid"))  # NOQA

    query = {"name": "simulated-lambda-phage-reads"}
    r = tmp_app.post(
        "/search_for_datasets",
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    datasets = json.loads(r.data)
    assert len(datasets) == 1
    assert datasets[0]["uuid"] == u"af6727bf-29c7-43dd-b42f-a5d7ede28337"
