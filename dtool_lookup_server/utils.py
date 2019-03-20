"""Utility functions."""

from sqlalchemy.sql import exists

from dtool_lookup_server import sql_db
from dtool_lookup_server.sql_models import (
    User,
    BaseURI,
    Dataset,
)


#############################################################################
# Generic helper functions
#############################################################################

def dataset_info_is_valid(dataset_info):
    """Return True if the dataset info is valid."""
    if "uuid" not in dataset_info:
        return False
    if "type" not in dataset_info:
        return False
    if "uri" not in dataset_info:
        return False
    if "name" not in dataset_info:
        return False
    if "base_uri" not in dataset_info:
        return False
    if dataset_info["type"] != "dataset":
        return False
    if len(dataset_info["uuid"]) != 36:
        return False
    if dataset_info["base_uri"].endswith("/"):
        return False
    return True


#############################################################################
# User helper functions
#############################################################################

def _get_user_obj(username_str):
    return User.query.filter_by(username=username_str).first()


def register_users(users):
    """Register a list of users in the system.

    Example input structure::

        [
            {"username": "magic.mirror", "is_admin": True},
            {"username": "snow.white", "is_admin": False},
            {"username": "dopey"},
            {"username": "sleepy"},
        ]

    If a user is already registered in the system it is skipped. To change the
    ``is_admin`` status of an existing user use the
    :func:`dtool_lookup_server.utils.set_user_is_admin`` function.
    """

    for user in users:
        username = user["username"]
        is_admin = user.get("is_admin", False)

        # Skip existing users.
        if sql_db.session.query(
            exists().where(User.username == username)
        ).scalar():
            continue

        user = User(username=username, is_admin=is_admin)
        sql_db.session.add(user)

    sql_db.session.commit()


def list_users():
    """Return list of users."""
    users = []
    for u in User.query.all():
        users.append(u.as_dict())
    return users


def get_user_info(username):
    """Return information about a user as a dictionary.

    Return None if the user does not exist.
    """
    user = User.query.filter_by(username=username).first()

    if user is None:
        return None

    return user.as_dict()


def list_datasets_by_user(username):
    """List the datasets the user has access to.

    Returns list of dicts if user is valid and has access to datasets.
    Returns empty list if user is valid but has not got access to any datasets.
    Returns None if user is invalid.
    """
    datasets = []
    user = _get_user_obj(username)
    if user is None:
        return None
    for base_uri in user.search_base_uris:
        for ds in base_uri.datasets:
            datasets.append(ds.as_dict())
    return datasets


#############################################################################
# Base URI helper functions
#############################################################################

def _get_base_uri_obj(base_uri_str):
    return BaseURI.query.filter_by(base_uri=base_uri_str).first()


def register_base_uri(base_uri):
    """Register a base URI in the dtool lookup server."""
    base_uri = BaseURI(base_uri=base_uri)
    sql_db.session.add(base_uri)
    sql_db.session.commit()


def list_base_uris():
    """List the base URIs in the dtool lookup server."""
    base_uris = []
    for bu in BaseURI.query.all():
        base_uris.append(bu.as_dict())
    return base_uris


#############################################################################
# Permission helper functions
#############################################################################

def update_permissions(permissions):
    """Rewrite permissions."""
    base_uri = _get_base_uri_obj(permissions["base_uri"])
    for username in permissions["users_with_search_permissions"]:
        user = _get_user_obj(username)
        if user is not None:
            user.search_base_uris.append(base_uri)
    for username in permissions["users_with_register_permissions"]:
        user = _get_user_obj(username)
        if user is not None:
            user.register_base_uris.append(base_uri)
    sql_db.session.commit()


def show_permissions(base_uri_str):
    """Return the permissions of on a base URI as a dictionary."""
    base_uri = _get_base_uri_obj(base_uri_str)
    return base_uri.as_dict()


#############################################################################
# Dataset SQL helper functions
#############################################################################

def register_dataset_admin_metadata(admin_metadata):
    """Register the admin metadata in the dataset SQL table."""
    base_uri = _get_base_uri_obj(admin_metadata["base_uri"])
    dataset = Dataset(
        uri=admin_metadata["uri"],
        base_uri_id=base_uri.id,
        uuid=admin_metadata["uuid"],
        name=admin_metadata["name"]
    )
    sql_db.session.add(dataset)
    sql_db.session.commit()


def get_admin_metadata_from_uri(uri):
    """Return the dataset SQL table row as dictionary."""
    dataset = Dataset.query.filter_by(uri=uri).first()

    if dataset is None:
        return None

    return dataset.as_dict()


def list_admin_metadata_in_base_uri(base_uri_str):
    """Return list of dictionaries with admin metadata from dataset SQL table.
    """
    base_uri = _get_base_uri_obj(base_uri_str)

    if base_uri is None:
        return None

    return [ds.as_dict() for ds in base_uri.datasets]


#############################################################################
# Dataset NoSQL helper functions
#############################################################################

def _num_datasets(collection):
    """Return the number of datasets in the mongodb collection."""
    return collection.count()


def register_dataset_descriptive_metadata(collection, dataset_info):
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
