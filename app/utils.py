"""Utility functions."""

import pymongo

def dataset_info_is_valid(dataset_info):
    """Return True if the dataset info is valid."""
    if "uuid" not in dataset_info:
        return False
    if "type" not in dataset_info:
        return False
    if "uri" not in dataset_info:
        return False
    if dataset_info["type"] != "dataset":
        return False
    if len(dataset_info["uuid"]) != 36:
        return False
    return True


def num_datasets(collection):
    """Return the number of datasets in the mongodb collection."""
    return collection.count()


def register_dataset(collection, dataset_info):
    """Register dataset info in the collection.

    If the "uuid" and "uri" are the same as another record in
    the mongodb collection a new record is not created, and
    the UUID is returned.

    Returns None if dataset_info is invalid.
    Returns UUID of dataset otherwise.
    """
    if not dataset_info_is_valid(dataset_info):
        return None

    # If a record with the same UUID and URI exists return the uuid
    # without adding a duplicate record.
    exists = collection.find_one({
        "uuid": dataset_info["uuid"],
        "uri": dataset_info["uri"]
    })

    if exists is None:
        collection.insert_one(dataset_info)

    # The MongoDB client dynamically updates the dataset_info dict
    # with and '_id' key. Remove it.
    if "_id" in dataset_info:
        del dataset_info["_id"]

    return dataset_info["uuid"]


def lookup_datasets(collection, uuid):
    """Return list of dataset info dictionaries with matching uuid."""
    result = []
    for info in collection.find({"uuid": uuid}):
        del info["_id"]
        result.append(info)
    return result
