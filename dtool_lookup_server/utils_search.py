"""Mongo search plugin module."""

import os

import dtoolcore.utils
import pymongo.errors

from pymongo import MongoClient


from dtool_lookup_server import SearchABC, ValidationError

from dtool_lookup_server.date_utils import (
    extract_created_at_as_datetime,
    extract_frozen_at_as_datatime,
)


VALID_MONGO_QUERY_KEYS = (
    "free_text",
    "creator_usernames",
    "base_uris",
    "uuids",
    "tags",
)

MONGO_QUERY_LIST_KEYS = (
    "creator_usernames",
    "base_uris",
    "uuids",
    "tags",
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

def _dict_to_mongo_query(query_dict):
    def _sanitise(query_dict):
        for key in list(query_dict.keys()):
            if key not in VALID_MONGO_QUERY_KEYS:
                del query_dict[key]
        for lk in MONGO_QUERY_LIST_KEYS:
            if lk in query_dict:
                if len(query_dict[lk]) == 0:
                    del query_dict[lk]

    def _deal_with_possible_or_statment(a_list, key):
        if len(a_list) == 1:
            return {key: a_list[0]}
        else:
            return {"$or": [{key: v} for v in a_list]}

    def _deal_with_possible_and_statement(a_list, key):
        if len(a_list) == 1:
            return {key: a_list[0]}
        else:
            return {key: {"$all": a_list}}

    _sanitise(query_dict)

    sub_queries = []
    if "free_text" in query_dict:
        sub_queries.append({"$text": {"$search": query_dict["free_text"]}})
    if "creator_usernames" in query_dict:
        sub_queries.append(
            _deal_with_possible_or_statment(
                query_dict["creator_usernames"], "creator_username"
            )
        )
    if "base_uris" in query_dict:
        sub_queries.append(
            _deal_with_possible_or_statment(query_dict["base_uris"], "base_uri")  # NOQA
        )
    if "uuids" in query_dict:
        sub_queries.append(_deal_with_possible_or_statment(query_dict["uuids"], "uuid"))  # NOQA
    if "tags" in query_dict:
        sub_queries.append(
            _deal_with_possible_and_statement(query_dict["tags"], "tags")
        )

    if len(sub_queries) == 0:
        return {}
    elif len(sub_queries) == 1:
        return sub_queries[0]
    else:
        return {"$and": [q for q in sub_queries]}


class MongoSearch(SearchABC):
    """Mongo implementation of the search plugin."""

    def init_app(self, app):
        try:
            self._mongo_uri = app.config["SEARCH_MONGO_URI"]
            self.client = MongoClient(self._mongo_uri)
        except KeyError:
            raise(RuntimeError("Please set the SEARCH_MONGO_URI environment variable"))  # NOQA

        try:
            self._mongo_db = app.config["SEARCH_MONGO_DB"]
            self.db = self.client[self._mongo_db]
        except KeyError:
            raise(RuntimeError("Please set the SEARCH_MONGO_DB environment variable"))  # NOQA

        try:
            self._mongo_collection = app.config["SEARCH_MONGO_COLLECTION"]
            self.collection = self.db[self._mongo_collection]
        except KeyError:
            raise(RuntimeError("Please set the SEARCH_MONGO_COLLECTION environment variable"))  # NOQA

        # Enable free text searching.
        # According to the Mongo documenation indexes will not be regenerated
        # if they already exists so it should be safe to run the command below
        # every time the class is instanciated.
        # https://www.mongodb.com/docs/manual/reference/method/db.collection.createIndex/#recreating-an-existing-index  # NOQA
        self.collection.create_index([("$**", pymongo.TEXT)])

    def register_dataset(self, dataset_info):
        try:
            return _register_dataset_descriptive_metadata(self.collection, dataset_info)
        except pymongo.errors.DocumentTooLarge as e:
            raise (ValidationError("Dataset has too much metadata: {}".format(e)))

    def search(self, query):

        # Deal with edge case where a user has no access to any base URIs.
        if len(query["base_uris"]) == 0:
            return []

        mongo_query = _dict_to_mongo_query(query)

        cx = self.collection.find(
            mongo_query,
            {
                "_id": False,
                "readme": False,
                "manifest": False,
                "annotations": False,
            },
        )

        datasets = []
        for ds in cx:
            # Convert datetime object to float timestamp.
            for key in ("created_at", "frozen_at"):
                datetime_obj = ds[key]
                ds[key] = dtoolcore.utils.timestamp(datetime_obj)

            datasets.append(ds)

        return datasets

    def lookup_uris(self, uuid, base_uris):

        # Deal with edge case where a user has no access to any base URIs.
        if len(base_uris) == 0:
            return []

        mongo_query = {
            "uuid": uuid,
            "$or": [{"base_uri": v} for v in base_uris]
        }
        cx = self.collection.find(
            mongo_query,
            {
                "_id": False,
                "uri": True,
                "base_uri": True,
                "uuid": True,
                "name": True
            },
        )

        datasets = []
        for ds in cx:
            datasets.append(ds)

        return datasets
