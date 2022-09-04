"""Mongo search plugin module."""

import os

import dtoolcore.utils

from pymongo import MongoClient

from dtool_lookup_server import SearchABC


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

    def __init__(self):
        try:
            self._mongo_uri = os.environ["MONGO_URI"]
            self.client = MongoClient(self._mongo_uri)
        except KeyError:
            raise(RuntimeError("Please set the MONGO_URI environment variable"))

        try:
            self._mongo_db = os.environ["MONGO_DB"]
            self.db = self.client[self._mongo_db]
        except KeyError:
            raise(RuntimeError("Please set the MONGO_DB environment variable"))

        try:
            self._mongo_collection = os.environ["MONGO_COLLECTION"]
            self.collection = self.db[self._mongo_collection]
        except KeyError:
            raise(RuntimeError("Please set the MONGO_COLLECTION environment variable"))  # NOQA

    def register_dataset(self, dataset_info):
        pass

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

    def lookup_uris(self, uuid):
        pass
