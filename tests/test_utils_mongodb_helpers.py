"""Test mongodb utility helper functions."""

from pymongo import MongoClient
from operator import itemgetter


def test_mongodb_utilities_functional():

    from dtool_lookup_server.utils import (
        _register_dataset_descriptive_metadata,
        lookup_datasets,
        search_for_datasets,
    )

    db_name = "testing_db"
    client = MongoClient()
    db = client[db_name]
    collection = db["datasets"]
    try:

        # At the start the collection is empty.
        assert collection.count() == 0

        # It is possible to register dataset in the collection by supplying
        # the relevant information.
        info = {
            u"uuid": u"af6727bf-29c7-43dd-b42f-a5d7ede28337",
            u"type": u"dataset",
            u"uri": u"file:///tmp/a_dataset",
            u"name": u"a-dataset",
            u"readme": "readme content",
            u"base_uri": u"file:///tmp",
        }
        uuid = _register_dataset_descriptive_metadata(collection, info)
        assert "_id" not in info
        assert uuid == info["uuid"]
        assert collection.count() == 1

        # Trying to register the same dataset information twice results
        # in the function returning the uuid, but without adding another
        # entry to the mongo database.
        uuid = _register_dataset_descriptive_metadata(collection, info)
        assert uuid == info["uuid"]
        assert collection.count() == 1

        # Trying to register a dataset using invalid information results
        # in the function returning None.
        assert _register_dataset_descriptive_metadata(collection, {"not": "valid"}) is None  # NOQA

        # Register a second dataset.
        info_2 = {
            u"uuid": u"c58038a4-3a54-425e-9087-144d0733387f",
            u"type": u"dataset",
            u"uri": u"file:///tmp/another_dataset",
            u"name": u"another-dataset",
            u"readme": "readme content",
            u"base_uri": u"file:///tmp",
        }
        uuid_2 = _register_dataset_descriptive_metadata(collection, info_2)
        assert collection.count() == 2

        # The same dataset can be registered in more than one location.
        # Register a second dataset.
        info_2_alt = {
            u"uuid": u"c58038a4-3a54-425e-9087-144d0733387f",
            u"type": u"dataset",
            u"uri": u"s3://dtool-demo/c58038a4-3a54-425e-9087-144d0733387f",
            u"name": u"another-dataset",
            u"readme": "readme content",
            u"base_uri": u"s3://dtool-demo",
        }
        assert _register_dataset_descriptive_metadata(collection, info_2_alt) == uuid_2  # NOQA
        assert collection.count() == 3

        # One can lookup dataset information using the UUID. This returns
        # a list with all the matching entries.
        lookup_result = lookup_datasets(collection, uuid)
        assert len(lookup_result) == 1
        assert "_id" not in lookup_result[0]
        assert lookup_result == [info]

        lookup_result = lookup_datasets(collection, uuid_2)
        assert len(lookup_result) == 2
        assert sorted(lookup_result, key=itemgetter("uuid")) == sorted([info_2, info_2_alt], key=itemgetter("uuid"))  # NOQA

        search_result = search_for_datasets(collection, query={})
        assert len(search_result) == 3
        assert "_id" not in lookup_result[0]

        # Add a dataset with more metadata.
        info_3 = {
            u"uuid": u"d5c0d959-4d0d-4c51-a1da-57d5b750c24f",
            u"frozen_at": 1511195175,
            u"creator_username": u"olssont",
            u"type": u"dataset",
            u"name": u"chrX-rna-seq",
            u"readme": "readme content",
            u"uri": u"s3://test-dtool/d5c0d959-4d0d-4c51-a1da-57d5b750c24f",
            u"base_uri": u"s3://test-dtool"
        }
        _register_dataset_descriptive_metadata(collection, info_3)

        search_result = search_for_datasets(
            collection,
            query={"name": "chrX-rna-seq"}
        )
        assert len(search_result) == 1
        assert info_3 == search_result[0]

    finally:
        client.drop_database(db_name)
