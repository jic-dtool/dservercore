"""Utility functions."""


#############################################################################
# User helper functions
#############################################################################

from dtool_lookup_server import sql_db
from dtool_lookup_server.sql_models import User


def register_user(username, is_admin=False):
    """Register a user in the system."""
    user = User(username=username, is_admin=is_admin)
    sql_db.session.add(user)
    sql_db.session.commit()
    return user.id


def get_user_info(username):
    """Return information about a user as a dictionary.

    Return None if the user does not exist.
    """
    user = User.query.filter_by(username=username).first()

    if user is None:
        return None

    user_info = {
        "username": user.username,
        "is_admin": user.is_admin,
        "base_uris": []
    }
    return user_info


#############################################################################
# Dataset helper functions
#############################################################################

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

    query = {
        "uuid": dataset_info["uuid"],
        "uri": dataset_info["uri"]
    }

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


def lookup_datasets(collection, uuid):
    """Return list of dataset info dictionaries with matching uuid."""
    return [i for i in collection.find({"uuid": uuid}, {"_id": False})]


def search_for_datasets(collection, query):
    """Return list of dataset info dictionaries matching the query."""
    return [i for i in collection.find(query, {"_id": False})]
