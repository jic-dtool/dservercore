"""Utility functions."""

from datetime import datetime, date
import importlib
import json
from pkg_resources import iter_entry_points

from flask import current_app
from sqlalchemy.sql import exists

import dtoolcore.utils

from dtool_lookup_server import (
    sql_db,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    UnknownBaseURIError,
    __version__
)
from dtool_lookup_server.sql_models import (
    User,
    BaseURI,
    Dataset,
)
from dtool_lookup_server.config import Config


from dtool_lookup_server.date_utils import (
    extract_created_at_as_datetime,
    extract_frozen_at_as_datetime,
)


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


# These entrypoints might point to plugin modules with
# config objects to be serialized as part of the global server config:
DTOOL_LOOKUP_SERVER_PLUGIN_ENTRYPOINTS = ['extension', 'retrieve', 'search']


#############################################################################
# Private helper functions.
#############################################################################

def _serializable(obj):
    """Return string representation of object if object itself not json-serializable."""
    try:
        json.dumps(obj)
    except TypeError:
        return str(obj)
    else:
        return obj


def _json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type {} not serializable".format(type(obj)))


def _get_user_obj(username):
    return User.query.filter_by(username=username).first()


def _get_base_uri_obj(base_uri):
    return BaseURI.query.filter_by(base_uri=base_uri).first()


#############################################################################
# Public helper functions.
#############################################################################

def obj_to_dict(obj, exclusions=[]):
    """Convert all-upper-case entries in dict-like object to dict and exclude
       certain keys. """
    d = dict()
    for k, v in obj.items():
        # select only capitalized fields
        if k.upper() == k and k not in exclusions:
            d[k] = _serializable(v)
        elif k.upper() == k and k in exclusions:
            d[k] = "***" # obfuscate secret
    return d


def obj_to_lowercase_key_dict(obj, exclusions=[]):
    """Convert all-upper-case keys in dict-like object to all-lower-case keys
       dict and exclude certain keys. """
    d = obj_to_dict(obj, exclusions=exclusions)
    return {k.lower(): v for k, v in d.items()}


def versions_to_dict():
    """Dumps installed components and their versions to dictionary, i.e.

        {
            'dtool_lookup_server': '0.17.2',
            'dtool_lookup_server_retrieve_plugin_mongo': '0.1.0',
            'dtool_lookup_server_search_plugin_mongo': '0.1.0'
        }
   """

    versions_dict = {'dtool_lookup_server': __version__}
    for ep_group in DTOOL_LOOKUP_SERVER_PLUGIN_ENTRYPOINTS:
        for ep in iter_entry_points("dtool_lookup_server.{}".format(ep_group)):
            module_name = ep.module_name.split(".")[0]

            # import module
            try:
                plugin_module = importlib.import_module(module_name)
            except ImportError as exc:
                # plugin import failed, this should not happen
                continue

            versions_dict[module_name] = getattr(plugin_module, '__version__', None)

    return versions_dict


#############################################################################
# Generally useful dtool helper functions.
#############################################################################

def generate_dataset_info(dataset, base_uri):
    """Return dictionary with dataset info."""
    dataset_info = dataset._admin_metadata
    dataset_info["uri"] = dataset.uri
    dataset_info["base_uri"] = base_uri

    # Add the readme info.
    dataset_info["readme"] = dataset.get_readme_content()

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

    # Set total number if items
    dataset_info["number_of_items"] = len(dataset.identifiers)

    # Compute size of dataset
    dataset_info["size_in_bytes"] = \
        sum([dataset.item_properties(i)["size_in_bytes"]
             for i in dataset.identifiers])

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
        raise (AuthenticationError())
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
        if sql_db.session.query(exists().where(User.username == username)).scalar():  # NOQA
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

        for sqlalch_user_obj in (
            sql_db.session.query(User).filter_by(username=username).all()
        ):  # NOQA
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

        for sqlalch_user_obj in (
            sql_db.session.query(User).filter_by(username=username).all()
        ):  # NOQA
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
        selected_uris = [str(bu) for bu in query["base_uris"] if bu in allowed_uris]  # NOQA
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

    return current_app.search.search(query)


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
    query = (
        sql_db.session.query(Dataset, User)
        .join(User.search_base_uris)
        .filter(Dataset.uuid == uuid)
        .filter(User.username == username)
        .filter(BaseURI.id == Dataset.base_uri_id)
        .all()
    )

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
        raise (ValidationError("Base URI {} not registered".format(base_uri)))
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
    if len(str(dataset_info["uuid"])) != 36:
        return False

    # Ensure that the base URI has had any trailing slash removed.
    if dataset_info["base_uri"].endswith("/"):
        return False

    return True


def register_dataset_admin_metadata(admin_metadata):
    """Register the admin metadata in the dataset SQL table."""
    base_uri = get_base_uri_obj(admin_metadata["base_uri"])

    frozen_at = extract_frozen_at_as_datetime(admin_metadata)
    created_at = extract_created_at_as_datetime(admin_metadata)

    try:
        number_of_items = admin_metadata["number_of_items"]
    except KeyError:
        number_of_items = None

    try:
        size_in_bytes = admin_metadata["size_in_bytes"]
    except KeyError:
        size_in_bytes = None

    dataset = Dataset(
        uri=admin_metadata["uri"],
        base_uri_id=base_uri.id,
        uuid=str(admin_metadata["uuid"]),
        name=admin_metadata["name"],
        creator_username=admin_metadata["creator_username"],
        frozen_at=frozen_at,
        created_at=created_at,
        number_of_items=number_of_items,
        size_in_bytes=size_in_bytes,
    )
    sql_db.session.add(dataset)
    sql_db.session.commit()


def register_dataset(dataset_info):
    """Register a dataset in the lookup server."""
    if not dataset_info_is_valid(dataset_info):
        raise (ValidationError("Dataset info not valid: {}".format(dataset_info)))  # NOQA

    base_uri = dataset_info["base_uri"]
    if not base_uri_exists(base_uri):
        raise (ValidationError("Base URI is not registered: {}".format(base_uri)))  # NOQA

    # Take a copy as register_dataset_descriptive_metadata makes
    # changes to the dictionary, in particular it changes the
    # types of the dates to datetime objects.
    current_app.search.register_dataset(dataset_info.copy())
    current_app.retrieve.register_dataset(dataset_info.copy())
    for ex in current_app.custom_extensions:
        ex.register_dataset(dataset_info.copy())

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


def list_admin_metadata_in_base_uri(base_uri_str):
    """Return list of dictionaries with admin metadata from dataset SQL table."""  # NOQA
    base_uri = get_base_uri_obj(base_uri_str)

    if base_uri is None:
        return None

    return [ds.as_dict() for ds in base_uri.datasets]


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
        raise (UnknownBaseURIError())

    if base_uri not in user.search_base_uris:
        raise (AuthorizationError())

    return current_app.retrieve.get_readme(uri)


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
        raise (UnknownBaseURIError())

    if base_uri not in user.search_base_uris:
        raise (AuthorizationError())

    return current_app.retrieve.get_manifest(uri)


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
        raise (UnknownBaseURIError())

    if base_uri not in user.search_base_uris:
        raise (AuthorizationError())

    return current_app.retrieve.get_annotations(uri)
