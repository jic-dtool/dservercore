"""Utility functions."""

from datetime import datetime, date
import importlib
import json
from pkg_resources import iter_entry_points

import yaml
from sqlalchemy.sql import exists

import pymongo.errors

import dtoolcore.utils

from dtool_lookup_server import (
    mongo,
    sql_db,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    UnknownBaseURIError,
    UnknownURIError,
    MONGO_COLLECTION,
)
from dtool_lookup_server.sql_models import (
    User,
    BaseURI,
    Dataset,
)
from dtool_lookup_server.config import Config

DATASET_INFO_REQUIRED_KEYS = (
    "uuid",
    "base_uri",
    "uri",
    "name",
    "type",
    "readme",
    "manifest",
    "creator_username",
    "frozen_at",
    "annotations",
    "tags",
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


#############################################################################
# Private helper functions.
#############################################################################

def _json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type {} not serializable".format(type(obj)))


def _get_user_obj(username):
    return User.query.filter_by(username=username).first()


def _get_base_uri_obj(base_uri):
    return BaseURI.query.filter_by(base_uri=base_uri).first()


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
                query_dict["creator_usernames"],
                "creator_username"
            )
        )
    if "base_uris" in query_dict:
        sub_queries.append(
            _deal_with_possible_or_statment(
                query_dict["base_uris"],
                "base_uri"
            )
        )
    if "uuids" in query_dict:
        sub_queries.append(
            _deal_with_possible_or_statment(
                query_dict["uuids"],
                "uuid"
            )
        )
    if "tags" in query_dict:
        sub_queries.append(
            _deal_with_possible_and_statement(
                query_dict["tags"],
                "tags"
            )
        )

    if len(sub_queries) == 0:
        return {}
    elif len(sub_queries) == 1:
        return sub_queries[0]
    else:
        return {"$and": [q for q in sub_queries]}


#############################################################################
# Generally useful dtool helper functions.
#############################################################################

def config_to_dict(username):
    # Authenticate the user.
    get_user_obj(username)

    core_config = Config.to_dict()
    plugin_config = {}

    # Iterate over all registered blueprints
    # and get per-plugin configs if implemented.
    # All plugins are expected to be top-level modules.
    for ep in iter_entry_points("dtool_lookup_server.blueprints"):
        module_name = ep.module_name.split(".")[0]
        if module_name not in plugin_config:
            try:
                plugin_module = importlib.import_module(module_name)
            except ImportError as exc:
                # plugin import failed, this should not happen
                plugin_config[module_name] = str(exc)
                continue

            try:
                plugin_config[
                    module_name] = plugin_module.config.Config.to_dict()
            except AttributeError as exc:
                # plugin did not implement config.Config.to_dict properly
                plugin_config[module_name] = str(exc)
                continue

    # check for overlap between core config keys and plugin names
    if len(set(core_config.keys()) & set(plugin_config.keys())) > 0:
        raise ValueError(
            "Plugin module names and core server config keys must not overlap."
        )

    all_config = core_config
    if len(plugin_config) > 0:
        all_config.update(plugin_config)
    return all_config


def generate_dataset_info(dataset, base_uri):
    """Return dictionary with dataset info."""
    dataset_info = dataset._admin_metadata
    dataset_info["uri"] = dataset.uri
    dataset_info["base_uri"] = base_uri

    # Add the readme info.
    readme_info = yaml.load(
        dataset.get_readme_content(),
        Loader=yaml.FullLoader
    )
    dataset_info["readme"] = readme_info

    # Add the manifest.
    dataset_info["manifest"] = dataset._manifest

    # Add the annotations.
    annotations = {}
    for annotation_name in dataset.list_annotation_names():
        annotations[annotation_name] = dataset.get_annotation(annotation_name)
    dataset_info["annotations"] = annotations

    # Add the tags.
    tags = dataset.list_tags()
    dataset_info["tags"] = tags

    # Clean up datetime.data.
    dataset_info_json_str = json.dumps(dataset_info, default=_json_serial)
    dataset_info = json.loads(dataset_info_json_str)

    return dataset_info


#############################################################################
# User helper functions
#############################################################################

def user_exists(username):
    if _get_user_obj(username) is None:
        return False
    return True


def get_user_obj(username):
    user = _get_user_obj(username)
    if user is None:
        raise(AuthenticationError())
    return user


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
    ``is_admin`` status of an existing user use the :func:`.update_users``
    function. The ``is_admin`` status defaults to False.
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


def delete_users(users):
    """Delete a list of users in the system.

    Example input structure::

        [
            {"username": "magic.mirror", "is_admin": True},
            {"username": "snow.white", "is_admin": False},
            {"username": "dopey"},
            {"username": "sleepy"},
        ]

    If a user is missing in the system it is skipped.  Only the "username" key
    is used to identify a user, any other keys, such as "is_admin", are
    ignored.  The list of dictionary input argument is used to be consistent
    with the :func:`.list_users`` and the :func:`register_users` functions.
    """
    for user in users:
        username = user["username"]

        for sqlalch_user_obj in sql_db.session.query(User).filter_by(username=username).all():  # NOQA
            sql_db.session.delete(sqlalch_user_obj)

    sql_db.session.commit()


def update_users(users):
    """Update a list of users in the system.

    Example input structure::

        [
            {"username": "magic.mirror", "is_admin": True},
            {"username": "snow.white", "is_admin": False},
            {"username": "dopey"},
            {"username": "sleepy"},
        ]

    If a user is missing in the system it is skipped. The ``is_admin`` status
    defaults to False.
    """
    for user in users:
        username = user["username"]
        is_admin = user.get("is_admin", False)

        for sqlalch_user_obj in sql_db.session.query(User).filter_by(username=username).all():  # NOQA
            sqlalch_user_obj.is_admin = is_admin

    sql_db.session.commit()


def get_user_info(username):
    """Return information about a user as a dictionary.

    Return None if the user does not exist.
    """
    user = User.query.filter_by(username=username).first()

    if user is None:
        return None

    return user.as_dict()


#############################################################################
# Dataset list/search/lookup helper functions.
#############################################################################

def list_datasets_by_user(username):
    """List the datasets the user has access to.

    Returns list of dicts if user is valid and has access to datasets.
    Returns empty list if user is valid but has not got access to any datasets.
    Raises AuthenticationError if user is invalid.
    """
    user = get_user_obj(username)

    datasets = []
    for base_uri in user.search_base_uris:
        for ds in base_uri.datasets:
            datasets.append(ds.as_dict())
    return datasets


def _preprocess_privileges(username, query):
    """Preprocess a query dict according to per-user privileges."""
    user = get_user_obj(username)

    # Deal with base URIs. If not specified on the query add the ones that the
    # user has search privileges on. If specified filter out any that the user
    # does not have search privileges on.
    allowed_uris = [bu.base_uri for bu in user.search_base_uris]
    if "base_uris" not in query:
        query["base_uris"] = allowed_uris
    else:
        selected_uris = [
            str(bu) for bu in query["base_uris"]
            if bu in allowed_uris
        ]
        query["base_uris"] = selected_uris

    return query


def preprocess_query_base_uris(username, query):
    """Return query with appropriate base URIs.

    If no base URIs are in the query add all the allowed ones.
    If base URIs are provided only include the ones allowed.
    """
    return _preprocess_privileges(username, query)


def search_datasets_by_user(username, query):
    """Search the datasets the user has access to.

    Valid keys for the query are: creator_usernames, base_uris, free_text.  If
    the query dictionary is empty all datasets, that a user has access to, are
    returned.

    :param username: username
    :param query: dictionary specifying query
    :returns: List of dicts if user is valid and has access to datasets.
              Empty list if user is valid but has not got access to any
              datasets.
    :raises: AuthenticationError if user is invalid.
    """

    query = preprocess_query_base_uris(username, query)
    # If there are no base URIs at this point it means that the user is not
    # allowed to search for anything.
    if len(query["base_uris"]) == 0:
        return []

    datasets = []
    mongo_query = _dict_to_mongo_query(query)
    cx = mongo.db[MONGO_COLLECTION].find(
        mongo_query,
        {
            "_id": False,
            "readme": False,
            "manifest": False,
            "annotations": False,
        }
    )
    for ds in cx:

        # Convert datetime object to float timestamp.
        for key in ("created_at", "frozen_at"):
            datetime_obj = ds[key]
            ds[key] = dtoolcore.utils.timestamp(datetime_obj)

        datasets.append(ds)
    return datasets


def summary_of_datasets_by_user(username):
    """Return summary information of datasets the user has access to.

    Return dictionary of summary information.
    Raises AuthenticationError if user is invalid.
    """

    # Get all the datasets the user has access to.
    datasets = search_datasets_by_user(username, query={})

    datasets_per_creator = {}
    datasets_per_base_uri = {}
    datasets_per_tag = {}

    for ds in datasets:
        user = ds["creator_username"]
        uri = ds["base_uri"]
        datasets_per_creator[user] = datasets_per_creator.get(user, 0) + 1
        datasets_per_base_uri[uri] = datasets_per_base_uri.get(uri, 0) + 1

        # All datasets should have the "tags" key. However, it could be the
        # case that a dataset in the database prior to version 0.14.0 fails
        # to be re-indexed. In this case it would be left without having tags
        # added to it. In the below we therefore check to make sure that it is
        # present before we try to use it.
        if "tags" in ds:
            for tag in ds["tags"]:
                datasets_per_tag[tag] = datasets_per_tag.get(tag, 0) + 1

    summary = {
        "number_of_datasets": len(datasets),
        "creator_usernames": sorted(datasets_per_creator.keys()),
        "base_uris": sorted(datasets_per_base_uri.keys()),
        "datasets_per_creator": datasets_per_creator,
        "datasets_per_base_uri": datasets_per_base_uri,
        "tags": sorted(datasets_per_tag.keys()),
        "datasets_per_tag": datasets_per_tag,
    }

    return summary


def lookup_datasets_by_user_and_uuid(username, uuid):
    """Return list of dataset with matching uuid.

    Returns list of dicts if user is valid and has access to datasets.
    Returns empty list if user is valid but has not got access to any datasets.
    Raises AuthenticationError if user is invalid.
    """
    user = get_user_obj(username)

    datasets = []
    query = sql_db.session.query(Dataset, User)  \
        .join(User.search_base_uris)  \
        .filter(Dataset.uuid == uuid)  \
        .filter(User.username == username)  \
        .filter(BaseURI.id == Dataset.base_uri_id)  \
        .all()

    for ds, user in query:
        datasets.append(ds.as_dict())

    return datasets


#############################################################################
# Base URI helper functions
#############################################################################

def base_uri_exists(base_uri):
    """Return True if the base URI has been registered."""
    if _get_base_uri_obj(base_uri) is None:
        return False
    return True


def get_base_uri_obj(base_uri):
    """Return SQLAlchemy BaseURI object."""
    base_uri_obj = _get_base_uri_obj(base_uri)
    if base_uri_obj is None:
        raise(ValidationError(
            "Base URI {} not registered".format(base_uri)
        ))
    return base_uri_obj


def register_base_uri(base_uri):
    """Register a base URI in the dtool lookup server."""
    base_uri = dtoolcore.utils.sanitise_uri(base_uri)
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

def get_permission_info(base_uri_str):
    """Return the permissions of on a base URI as a dictionary."""
    base_uri = get_base_uri_obj(base_uri_str)
    return base_uri.as_dict()


def update_permissions(permissions):
    """Rewrite permissions."""
    base_uri = get_base_uri_obj(permissions["base_uri"])

    # Clear all the existing permissions.
    base_uri.search_users = []
    base_uri.register_users = []

    for username in permissions["users_with_search_permissions"]:
        if user_exists(username):
            user = get_user_obj(username)
            base_uri.search_users.append(user)

    for username in permissions["users_with_register_permissions"]:
        if user_exists(username):
            user = get_user_obj(username)
            base_uri.register_users.append(user)

    sql_db.session.commit()


#############################################################################
# Register dataset helper functions
#############################################################################

def dataset_info_is_valid(dataset_info):
    """Return True if the dataset info is valid."""

    # Ensure that all the required keys are present.
    for key in DATASET_INFO_REQUIRED_KEYS:
        if key not in dataset_info:
            return False

    # Ensure that it is a "dataset" and not a "protodataset".
    if dataset_info["type"] != "dataset":
        return False

    # Ensure that the UUID has the correct number of characters.
    if len(dataset_info["uuid"]) != 36:
        return False

    # Ensure that the base URI has had any trailing slash removed.
    if dataset_info["base_uri"].endswith("/"):
        return False

    return True


def _extract_created_at_as_datetime(admin_metadata):
    """Return created_at as datetime
    Use frozen_at if created_at is missing.
    Deal with some created_at values being strings.
    """
    try:
        created_at = admin_metadata["created_at"]
    except KeyError:
        created_at = admin_metadata["frozen_at"]
    created_at = float(created_at)
    return datetime.utcfromtimestamp(created_at)


def _extract_frozen_at_as_datatime(admin_metadata):
    frozen_at = admin_metadata["frozen_at"]
    frozen_at = float(frozen_at)
    return datetime.utcfromtimestamp(frozen_at)


def register_dataset_admin_metadata(admin_metadata):
    """Register the admin metadata in the dataset SQL table."""
    base_uri = get_base_uri_obj(admin_metadata["base_uri"])

    frozen_at = _extract_frozen_at_as_datatime(admin_metadata)
    created_at = _extract_created_at_as_datetime(admin_metadata)

    dataset = Dataset(
        uri=admin_metadata["uri"],
        base_uri_id=base_uri.id,
        uuid=admin_metadata["uuid"],
        name=admin_metadata["name"],
        creator_username=admin_metadata["creator_username"],
        frozen_at=frozen_at,
        created_at=created_at
    )
    sql_db.session.add(dataset)
    sql_db.session.commit()


def register_dataset_descriptive_metadata(dataset_info):

    # Validate that the base URI exists.
    get_base_uri_obj(dataset_info["base_uri"])

    collection = mongo.db[MONGO_COLLECTION]
    _register_dataset_descriptive_metadata(collection, dataset_info)


def _register_dataset_descriptive_metadata(collection, dataset_info):
    """Register dataset info in the collection.

    If the "uuid" and "uri" are the same as another record in
    the mongodb collection a new record is not created, and
    the UUID is returned.

    Returns None if dataset_info is invalid.
    Returns UUID of dataset otherwise.
    """
    if not dataset_info_is_valid(dataset_info):
        return None

    frozen_at = _extract_frozen_at_as_datatime(dataset_info)
    created_at = _extract_created_at_as_datetime(dataset_info)

    dataset_info["frozen_at"] = frozen_at
    dataset_info["created_at"] = created_at

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


def register_dataset(dataset_info):
    """Register a dataset in the lookup server."""
    if not dataset_info_is_valid(dataset_info):
        raise(ValidationError(
            "Dataset info not valid: {}".format(dataset_info)
        ))

    base_uri = dataset_info["base_uri"]
    if not base_uri_exists(base_uri):
        raise(ValidationError(
            "Base URI is not registered: {}".format(base_uri)
        ))

    try:
        # Take a copy as register_dataset_descriptive_metadata makes
        # changes to the dictionary, in particular it changes the
        # types of the dates to datetime objects.
        register_dataset_descriptive_metadata(dataset_info.copy())
    except pymongo.errors.DocumentTooLarge as e:
        raise(ValidationError(
            "Dataset has too much metadata: {}".format(e)
        ))

    if get_admin_metadata_from_uri(dataset_info["uri"]) is None:
        register_dataset_admin_metadata(dataset_info)

    return dataset_info["uri"]


#############################################################################
# Dataset information retrieval helper functions.
#############################################################################

def get_admin_metadata_from_uri(uri):
    """Return the dataset SQL table row as dictionary."""
    dataset = Dataset.query.filter_by(uri=uri).first()

    if dataset is None:
        return None

    return dataset.as_dict()


def get_readme_from_uri_by_user(username, uri):
    """Return the readme.

    :param username: username
    :param uri: dataset URI
    :returns: dataset readme
    :raises: AuthenticationError if user is invalid.
             AuthorizationError if the user has not got permissions to read
             content in the base URI
             UnknownBaseURIError if the base URI has not been registered.
             UnknownURIError if the URI is not available to the user.
    """
    user = get_user_obj(username)

    base_uri_str = uri.rsplit("/", 1)[0]
    base_uri = _get_base_uri_obj(base_uri_str)
    if base_uri is None:
        raise(UnknownBaseURIError())

    if base_uri not in user.search_base_uris:
        raise(AuthorizationError())

    collection = mongo.db[MONGO_COLLECTION]
    item = collection.find_one({"uri": uri})
    if item is None:
        raise(UnknownURIError())
    return item["readme"]


def get_annotations_from_uri_by_user(username, uri):
    """Return the annotations.

    :param username: username
    :param uri: dataset URI
    :returns: dataset annotations
    :raises: AuthenticationError if user is invalid.
             AuthorizationError if the user has not got permissions to read
             content in the base URI
             UnknownBaseURIError if the base URI has not been registered.
             UnknownURIError if the URI is not available to the user.
    """
    user = get_user_obj(username)

    base_uri_str = uri.rsplit("/", 1)[0]
    base_uri = _get_base_uri_obj(base_uri_str)
    if base_uri is None:
        raise(UnknownBaseURIError())

    if base_uri not in user.search_base_uris:
        raise(AuthorizationError())

    collection = mongo.db[MONGO_COLLECTION]
    item = collection.find_one({"uri": uri})
    if item is None:
        raise(UnknownURIError())
    return item["annotations"]


def get_manifest_from_uri_by_user(username, uri):
    """Return the manifest.

    :param username: username
    :param uri: dataset URI
    :returns: dataset manifest
    :raises: AuthenticationError if user is invalid.
             AuthorizationError if the user has not got permissions to read
             content in the base URI
             UnknownBaseURIError if the base URI has not been registered.
             UnknownURIError if the URI is not available to the user.
    """
    user = get_user_obj(username)

    base_uri_str = uri.rsplit("/", 1)[0]
    base_uri = _get_base_uri_obj(base_uri_str)
    if base_uri is None:
        raise(UnknownBaseURIError())

    if base_uri not in user.search_base_uris:
        raise(AuthorizationError())

    collection = mongo.db[MONGO_COLLECTION]
    item = collection.find_one({"uri": uri})
    if item is None:
        raise(UnknownURIError())
    return item["manifest"]


def list_admin_metadata_in_base_uri(base_uri_str):
    """Return list of dictionaries with admin metadata from dataset SQL table.
    """
    base_uri = get_base_uri_obj(base_uri_str)

    if base_uri is None:
        return None

    return [ds.as_dict() for ds in base_uri.datasets]
