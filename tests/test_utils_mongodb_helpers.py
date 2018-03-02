"""Test mongodb utility helper functions."""

from pymongo import MongoClient


def test_mongodb_utiliites_functional():

    from app.utils import (
        num_datasets,
        register_dataset,
        lookup_datasets,
    )

    db_name = "testing_db"
    client = MongoClient()
    db = client[db_name]
    try:

        # At the start the collection is empty.
        collection = db["datasets"]
        assert num_datasets(collection) == 0

        # It is possible to register dataset in the collection by supplying
        # the relevant information.
        info = {
            u"uuid": u"af6727bf-29c7-43dd-b42f-a5d7ede28337",
            u"type": u"dataset",
            u"uri": u"file:///tmp/a_dataset"
        }
        uuid = register_dataset(collection, info)
        assert "_id" not in info
        assert uuid == info["uuid"]
        assert num_datasets(collection) == 1

        # Trying to register the same dataset information twice results
        # in the function returning the uuid, but without adding another
        # entry to the mongo database.
        uuid = register_dataset(collection, info)
        assert uuid == info["uuid"]
        assert num_datasets(collection) == 1

        # Trying to register a dataset using invalid information results
        # in the function returning None.
        assert register_dataset(collection, {"not": "valid"}) is None

        # Register a second dataset.
        info_2 = {
            u"uuid": u"c58038a4-3a54-425e-9087-144d0733387f",
            u"type": u"dataset",
            u"uri": u"file:///tmp/another_dataset"
        }
        uuid_2 = register_dataset(collection, info_2)
        assert num_datasets(collection) == 2

        # The same dataset can be registered in more than one location.
        # Register a second dataset.
        info_2_alt = {
            u"uuid": u"c58038a4-3a54-425e-9087-144d0733387f",
            u"type": u"dataset",
            u"uri": u"s3:/test-dtool/c58038a4-3a54-425e-9087-144d0733387f"
        }
        assert register_dataset(collection, info_2_alt) == uuid_2
        assert num_datasets(collection) == 3

        # One can lookup dataset information using the UUID. This returns
        # a list with all the matching entries.
        lookup_result = lookup_datasets(collection, uuid)
        assert len(lookup_result) == 1
        assert "_id" not in lookup_result[0]
        assert lookup_result == [info]

        lookup_result = lookup_datasets(collection, uuid_2)
        assert len(lookup_result) == 2
        assert sorted(lookup_result) == sorted([info_2, info_2_alt])

    finally:
        client.drop_database(db_name)
