"""Mongo retrieve plugin module."""

import os

import dtoolcore.utils
import pymongo.errors

from pymongo import MongoClient

from dtool_lookup_server import RetrieveABC, ValidationError, UnknownURIError

from dtool_lookup_server.date_utils import (
    extract_created_at_as_datetime,
    extract_frozen_at_as_datatime,
)


def _register_dataset_descriptive_metadata(collection, dataset_info):
    """Register dataset info in the collection.

    If the "uuid" and "uri" are the same as another record in
    the mongodb collection a new record is not created, and
    the UUID is returned.

    Returns UUID of dataset otherwise.
    """

    # Make a copy to ensure that the original data strucutre does not
    # get mangled by the datetime replacements.
    dataset_info = dataset_info.copy()

    frozen_at = extract_frozen_at_as_datatime(dataset_info)
    created_at = extract_created_at_as_datetime(dataset_info)

    dataset_info["frozen_at"] = frozen_at
    dataset_info["created_at"] = created_at

    query = {"uuid": dataset_info["uuid"], "uri": dataset_info["uri"]}

    # If a record with the same UUID and URI exists return the uuid
    # without adding a duplicate record.
    exists = collection.find_one(query)

    if exists is None:
        collection.insert_one(dataset_info)
    else:
        collection.find_one_and_replace(query, dataset_info)

    # The MongoDB client dynamically updates the dataset_info dict
    # with and '_id' key. Remove it.
    if "_id" in dataset_info:
        del dataset_info["_id"]

    return dataset_info["uuid"]


class MongoRetrieve(RetrieveABC):
    """Mongo implementation of the retrieve module."""

    # The intput arguments to the below are only there to make it easier to
    # test the code. When plugged into the dtool-lookup-server these variables
    # will be parsed from the environment variables named:
    # MONGO_URI, MONGO_DB, and MONGO_COLLECTION.
    def __init__(self, mongo_uri=None, mongo_db=None, mongo_collection=None):
        if mongo_uri is None:
            try:
                self._mongo_uri = os.environ["MONGO_URI"]
                self.client = MongoClient(self._mongo_uri)
            except KeyError:
                raise(RuntimeError("Please set the MONGO_URI environment variable"))  # NOQA
        else:
            self.client = MongoClient(mongo_uri)

        if mongo_db is None:
            try:
                self._mongo_db = os.environ["MONGO_DB"]
                self.db = self.client[self._mongo_db]
            except KeyError:
                raise(RuntimeError("Please set the MONGO_DB environment variable"))  # NOQA
        else:
            self.db = self.client[mongo_db]

        if mongo_collection is None:
            try:
                self._mongo_collection = os.environ["MONGO_COLLECTION"]
                self.collection = self.db[self._mongo_collection]
            except KeyError:
                raise(RuntimeError("Please set the MONGO_COLLECTION environment variable"))  # NOQA
        else:
            self.collection = self.db[mongo_collection]

    def register_dataset(self, dataset_info):
        try:
            return _register_dataset_descriptive_metadata(self.collection, dataset_info)
        except pymongo.errors.DocumentTooLarge as e:
            raise (ValidationError("Dataset has too much metadata: {}".format(e)))

    def get_readme(self, uri):
        item = self.collection.find_one({"uri": uri})
        if item is None:
            raise (UnknownURIError())
        return item["readme"]

    def get_manifest(self, uri):
        item = self.collection.find_one({"uri": uri})
        if item is None:
            raise (UnknownURIError())
        return item["manifest"]

    def get_annotations(self, uri):
        item = self.collection.find_one({"uri": uri})
        if item is None:
            raise (UnknownURIError())
        return item["annotations"]