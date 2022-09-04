"""Mongo utility functions."""

import pymongo.errors

import dtoolcore.utils

from dtool_lookup_server import (
    mongo,
    ValidationError,
    UnknownURIError,
    MONGO_COLLECTION,
)

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


def _register_dataset_descriptive_metadata(collection, dataset_info):
    """Register dataset info in the collection.

    If the "uuid" and "uri" are the same as another record in
    the mongodb collection a new record is not created, and
    the UUID is returned.

    Returns UUID of dataset otherwise.
    """

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


def search_datasets_mongo(query):
    datasets = []
    mongo_query = _dict_to_mongo_query(query)
    cx = mongo.db[MONGO_COLLECTION].find(
        mongo_query,
        {
            "_id": False,
            "readme": False,
            "manifest": False,
            "annotations": False,
        },
    )
    for ds in cx:

        # Convert datetime object to float timestamp.
        for key in ("created_at", "frozen_at"):
            datetime_obj = ds[key]
            ds[key] = dtoolcore.utils.timestamp(datetime_obj)

        datasets.append(ds)
    return datasets


def register_dataset_descriptive_metadata_mongo(dataset_info):

    collection = mongo.db[MONGO_COLLECTION]
    try:
        return _register_dataset_descriptive_metadata(collection, dataset_info)
    except pymongo.errors.DocumentTooLarge as e:
        raise (ValidationError("Dataset has too much metadata: {}".format(e)))


def get_readme_from_uri_mongo(uri):
    collection = mongo.db[MONGO_COLLECTION]
    item = collection.find_one({"uri": uri})
    if item is None:
        raise (UnknownURIError())
    return item["readme"]


def get_annotations_from_uri_mongo(uri):
    collection = mongo.db[MONGO_COLLECTION]
    item = collection.find_one({"uri": uri})
    if item is None:
        raise (UnknownURIError())
    return item["annotations"]


def get_manifest_from_uri_mongo(uri):
    collection = mongo.db[MONGO_COLLECTION]
    item = collection.find_one({"uri": uri})
    if item is None:
        raise (UnknownURIError())
    return item["manifest"]
