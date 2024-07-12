"""Utility functions."""

from datetime import datetime, date
import importlib
import json
import logging
from pkg_resources import iter_entry_points

from flask import current_app
from flask_smorest.pagination import PaginationParameters
from sqlalchemy.sql import exists

import dtoolcore.utils

from dservercore import (
    sql_db,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    UnknownBaseURIError,
    UnknownURIError,
    __version__
)
from dservercore.sql_models import (
    User,
    BaseURI,
    Dataset,
)
from dservercore.sort import SortParameters, ASCENDING, DESCENDING


from dservercore.date_utils import (
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


DATASET_SORT_FIELDS = [
    "base_uri",
    "created_at",
    "creator_username",
    "frozen_at",
    "name",
    "uri",
    "uuid"
]


# These entrypoints might point to plugin modules with
# config objects to be serialized as part of the global server config:
DSERVER_PLUGIN_ENTRYPOINTS = ['extension', 'retrieve', 'search']


logger = logging.getLogger(__name__)


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


def _get_dataset_obj(uri):
    return Dataset.query.filter_by(uri=uri).first()


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
            'dservercore': '0.17.2',
            'dserver_retrieve_plugin_mongo': '0.1.0',
            'dserver_search_plugin_mongo': '0.1.0'
        }
   """

    versions_dict = {'dservercore': __version__}
    for ep_group in DSERVER_PLUGIN_ENTRYPOINTS:
        for ep in iter_entry_points("dservercore.{}".format(ep_group)):
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
    """Check whether user is registered in the system."""
    if _get_user_obj(username) is None:
        return False
    return True


def get_user_obj(username):
    """Retrieve User object from username."""
    user = _get_user_obj(username)
    if user is None:
        raise (AuthenticationError())
    return user


def register_user(username, data):
    """Register or update a single user in the system by replacing entry. Idempotent.

    Example input structure::

        {"is_admin": True},

    If a user is missing in the system it is skipped. The ``is_admin`` status
    defaults to False.
    """
    is_admin = data.get("is_admin", False)

    # User already exists, update
    if sql_db.session.query(exists().where(User.username == username)).scalar():
        for sqlalch_user_obj in (
            sql_db.session.query(User).filter_by(username=username).all()
        ):
            sqlalch_user_obj.is_admin = is_admin
    else:  # user does not exist yet, create
        user = User(username=username, is_admin=is_admin)
        sql_db.session.add(user)

    sql_db.session.commit()


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


def delete_user(username):
    """Delete a single user from the system."""
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

def _dataset_order_by_args(sort_parameters):
    """Convert SortParameters to SQLAlchemy sort argument for Dataset model."""

    order_by_args = []
    for field, order in sort_parameters.order.items():
        if not hasattr(Dataset, field):
            continue
        # special treatment for base_uri:
        # we want to sort by the string field BaseURI.base_uri, not by
        # the relationship field Dataset.base_uri
        if field in ['base_uri']:
            model = BaseURI
        else:
            model = Dataset
        if order == DESCENDING:
            order_by_args.append(getattr(model, field).desc())
        else:  # ascending
            order_by_args.append(getattr(model, field))
    return order_by_args


def list_datasets_by_user(username,
                          pagination_parameters: PaginationParameters = None,
                          sort_parameters: SortParameters = None):
    """List the datasets the user has access to.

    :param pagination_parameters: flask_smorest.pagination.PaginationParameters object, optional
    :param sort_parameters: dservercore.sort.SortParameters object, optional

    Returns list of dicts if user is valid and has access to datasets.
    Returns empty list if user is valid but has not got access to any datasets.
    Raises AuthenticationError if user is invalid.
    """
    user = get_user_obj(username)  # raises AuthenticationError

    query = (
        sql_db.session.query(Dataset, User)
        .join(User.search_base_uris)
        .filter(User.username == username)
        .filter(BaseURI.id == Dataset.base_uri_id)
    )

    if sort_parameters is not None:
        order_by_args = _dataset_order_by_args(sort_parameters)
        query = query.order_by(*order_by_args)

    if pagination_parameters is not None:
        pagination_parameters.item_count = query.count()
        queried_items = query.paginate(
            page=pagination_parameters.page,
            per_page=pagination_parameters.page_size,
            error_out=True).items
    else:
        queried_items = query.all()

    datasets = [ds for ds, user in queried_items]

    return datasets


def summary_of_datasets_by_user(username):
    """Return summary information of datasets the user has access to.

    Return dictionary of summary information.
    Raises AuthenticationError if user is invalid.
    """
    user = get_user_obj(username)  # raises AuthenticationError

    # Get all the datasets the user has access to.
    datasets = search_datasets_by_user(username, query={})

    datasets_per_creator = {}
    datasets_per_base_uri = {}
    datasets_per_tag = {}

    size_in_bytes_per_creator = {}
    size_in_bytes_per_base_uri = {}
    size_in_bytes_per_tag = {}

    total_size_in_bytes = 0

    for ds in datasets:
        user = ds["creator_username"]
        uri = ds["base_uri"]
        datasets_per_creator[user] = datasets_per_creator.get(user, 0) + 1
        datasets_per_base_uri[uri] = datasets_per_base_uri.get(uri, 0) + 1

        size_in_bytes_per_creator[user] = size_in_bytes_per_creator.get(user, 0) + ds["size_in_bytes"]
        size_in_bytes_per_base_uri[uri] = size_in_bytes_per_base_uri.get(uri, 0) + ds["size_in_bytes"]

        # All datasets should have the "tags" key. However, it could be the
        # case that a dataset in the database prior to version 0.14.0 fails
        # to be re-indexed. In this case it would be left without having tags
        # added to it. In the below we therefore check to make sure that it is
        # present before we try to use it.
        if "tags" in ds:
            for tag in ds["tags"]:
                datasets_per_tag[tag] = datasets_per_tag.get(tag, 0) + 1
                size_in_bytes_per_tag[tag] = size_in_bytes_per_tag.get(tag, 0) + ds["size_in_bytes"]

        total_size_in_bytes += ds["size_in_bytes"]

    summary = {
        "number_of_datasets": len(datasets),
        "total_size_in_bytes": total_size_in_bytes,
        "creator_usernames": sorted(datasets_per_creator.keys()),
        "base_uris": sorted(datasets_per_base_uri.keys()),
        "datasets_per_creator": datasets_per_creator,
        "size_in_bytes_per_creator": size_in_bytes_per_creator,
        "datasets_per_base_uri": datasets_per_base_uri,
        "size_in_bytes_per_base_uri": size_in_bytes_per_base_uri,
        "tags": sorted(datasets_per_tag.keys()),
        "datasets_per_tag": datasets_per_tag,
        "size_in_bytes_per_tag": size_in_bytes_per_tag
    }

    return summary


def lookup_datasets_by_user_and_uuid(username, uuid,
                                     pagination_parameters: PaginationParameters = None,
                                     sort_parameters: SortParameters = None):
    """Return list of dataset with matching uuid.

    Returns list of dicts if user is valid and has access to datasets.
    Returns empty list if user is valid but has not got access to any datasets.
    Raises AuthenticationError if user is invalid.
    """
    user = get_user_obj(username)  # raises AuthenticationError

    query = (
        sql_db.session.query(Dataset, User)
        .join(User.search_base_uris)
        .filter(Dataset.uuid == uuid)
        .filter(User.username == username)
        .filter(BaseURI.id == Dataset.base_uri_id)
    )

    if sort_parameters is not None:
        order_by_args = _dataset_order_by_args(sort_parameters)
        query = query.order_by(*order_by_args)

    if pagination_parameters is not None:
        pagination_parameters.item_count = query.count()
        queried_items = query.paginate(
            page=pagination_parameters.page,
            per_page=pagination_parameters.page_size,
            error_out=True).items
    else:
        queried_items = query.all()

    datasets = [ds for ds, user in queried_items]

    return datasets


def get_dataset_by_user_and_uri(username, uri):
    """Return single dataset with matching uri if user has rights to see it.

    Returns single Dataset if user is valid and has access to datasets.
    Returns None if user is valid but has not got access to the dataset.
    Raises AuthenticationError if user is invalid.
    """

    # datasets = []
    query = (
        sql_db.session.query(Dataset, User)
        .join(User.search_base_uris)
        .filter(Dataset.uri == uri)
        .filter(User.username == username)
        .filter(BaseURI.id == Dataset.base_uri_id)
        .all()
    )

    datasets = [ds for ds, user in query]

    if len(datasets) > 0:
        ret = datasets[0]
    else:
        ret = None

    return ret


#############################################################################
# Search plugin interface
#############################################################################

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


def search_datasets_by_user(username, query,
                            pagination_parameters: PaginationParameters = None,
                            sort_parameters: SortParameters = None):
    """Search the datasets the user has access to.

    Valid keys for the query are: creator_usernames, base_uris, free_text.  If
    the query dictionary is empty all datasets, that a user has access to, are
    returned.

    :param username: username
    :param query: dictionary specifying query
    :param pagination_parameters: flask_smorest.pagination.PaginationParameters object, optional
    :param sort_parameters: dservercore.sort.SortParameters object, optional
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

    return current_app.search.search(query,
                                     pagination_parameters=pagination_parameters,
                                     sort_parameters=sort_parameters)


#############################################################################
# Base URI helper functions
#############################################################################


def url_suffix_to_uri(url_suffix):
    """Translates a URL suffix like

            s3/bucket

    to a valid URI, e.g.

            s3://bucket
    """

    # first, make sure url_suffix isn't already a valid URI
    uri = url_suffix
    index = uri.find('://')
    if index == -1:  # not found
        uri = uri.replace('/', '://', 1)

    uri = dtoolcore.utils.sanitise_uri(uri)
    return uri


def uri_to_url_suffix(uri):
    """Translates a URI like

            s3://bucket

    to a URL suffix like

            s3/bucket
    """
    url_suffix = dtoolcore.utils.sanitise_uri(uri)

    # first, make sure uri has the :// separator, then replace with simple /
    index = url_suffix.find('://')
    if index != -1:  # not found
        url_suffix = url_suffix.replace('://', '/', 1)

    return url_suffix


def base_uri_exists(base_uri):
    """Return True if the base URI has been registered."""
    if _get_base_uri_obj(base_uri) is None:
        return False
    return True


def get_base_uri_obj(base_uri):
    """Return SQLAlchemy BaseURI object."""
    base_uri_obj = _get_base_uri_obj(base_uri)
    if base_uri_obj is None:
        raise (UnknownBaseURIError("Base URI {} not registered".format(base_uri)))
    return base_uri_obj


def register_base_uri(base_uri):
    """Register a base URI in dserver."""
    base_uri = dtoolcore.utils.sanitise_uri(base_uri)
    base_uri = BaseURI(base_uri=base_uri)

    sql_db.session.add(base_uri)
    sql_db.session.commit()


def delete_base_uri(base_uri):
    """Delete a base URI from dserver."""
    base_uri = dtoolcore.utils.sanitise_uri(base_uri)

    for sqlalch_base_uri_obj in (
        sql_db.session.query(BaseURI).filter_by(base_uri=base_uri).all()
    ):  # NOQA
        sql_db.session.delete(sqlalch_base_uri_obj)

    sql_db.session.commit()


def list_base_uris():
    """List the base URIs in dserver."""
    base_uris = []
    for bu in BaseURI.query.all():
        base_uris.append(bu.as_dict())
    return base_uris


#############################################################################
# Permission helper functions
#############################################################################


def get_permission_info(base_uri_str):
    """Return the permissions on a base URI as a dictionary."""
    base_uri = get_base_uri_obj(base_uri_str)
    return base_uri.as_dict()


def register_permissions(base_uri, permissions):
    """Register or update permissions on base_uri. Idempotent."""
    base_uri = get_base_uri_obj(base_uri)

    # Clear all the existing permissions.
    base_uri.search_users = []
    base_uri.register_users = []

    if "users_with_search_permissions" in permissions:
        for username in permissions["users_with_search_permissions"]:
            if user_exists(username):
                user = get_user_obj(username)
                base_uri.search_users.append(user)

    if "users_with_register_permissions" in permissions:
        for username in permissions["users_with_register_permissions"]:
            if user_exists(username):
                user = get_user_obj(username)
                base_uri.register_users.append(user)

    sql_db.session.commit()


#############################################################################
# Register dataset helper functions
#############################################################################


def dataset_uri_exists(uri):
    """Return True if the dataset URI has been registered."""
    if _get_dataset_obj(uri) is None:
        return False
    return True


def get_dataset_obj(uri):
    """Return SQLAlchemy Dataset object."""
    dataset_obj = _get_dataset_obj(uri)
    if dataset_obj is None:
        raise (UnknownURIError("URI {} not registered".format(uri)))
    return dataset_obj


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


def create_dataset_obj_from_admin_metadata(admin_metadata):
    """Create an object adhering to the Dataset model from a dict-like object admin_metadata."""

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
    return dataset


def register_dataset_admin_metadata(admin_metadata):
    """Update the admin metadata in the dataset SQL table by replacing a possibly existing dataset entry."""

    # first, validate dataset info
    new_dataset_entry = create_dataset_obj_from_admin_metadata(admin_metadata)

    uri = admin_metadata["uri"]

    # there must only be one object, as URI is the unique index
    sql_db.session.query(Dataset).filter_by(uri=uri).delete()

    sql_db.session.add(new_dataset_entry)
    sql_db.session.commit()

    return new_dataset_entry.uri


def delete_dataset_admin_metadata(uri):
    """Delete the admin metadata from the dataset SQL table.

    :param uri: URI of dataset entry to delete.
    :returns: URI of successfully deleted dataset entry"""

    # there must only be one object, as URI is the unique index
    for old_dataset_entry in (
            sql_db.session.query(Dataset).filter_by(uri=uri).all()
    ):
        sql_db.session.delete(old_dataset_entry)

    sql_db.session.commit()

    return uri


def register_dataset(dataset_info):
    """Put-update a dataset in the lookup server. Put is idempotent."""

    if not dataset_info_is_valid(dataset_info):
        raise (ValidationError("Dataset info not valid: {}".format(dataset_info)))  # NOQA

    base_uri = dataset_info["base_uri"]
    if not base_uri_exists(base_uri):
        raise (ValidationError("Base URI is not registered: {}".format(base_uri)))  # NOQA

    # Take a copy as register_dataset_descriptive_metadata makes
    # changes to the dictionary, in particular it changes the
    # types of the dates to datetime objects.
    # On the core search and retrieve plugins, we are strict. We expect them
    # to raise ValidationError on failure, we log those, and reraise
    try:
        if hasattr(current_app.search, "register_dataset"):
            current_app.search.register_dataset(dataset_info.copy())
        else:
            logger.warning("Search plugin has no method 'register_dataset'")
            logger.warning("Applied modifications to dataset entry '%s' will not take effect in search database.'",
                           dataset_info["uri"])
    except ValidationError as message:
        # Instead of reporting the error with the logging module, we will want
        # to do some bookkeeping on registration errors per URI in the
        # core SQL db
        logger.error(message)
        raise

    try:
        if hasattr(current_app.retrieve, "register_dataset"):
            current_app.retrieve.register_dataset(dataset_info.copy())
        else:
            logger.warning("Retrieve plugin has no method 'register_dataset'")
            logger.warning("Applied modifications to dataset entry '%s' will not take effect in retrieve database.'",
                           dataset_info["uri"])
    except ValidationError as message:
        logger.error(message)
        raise

    # On any other optional extension, we want to be lenient. We still
    # want to keep track of any error, but the registration should not fail.
    for ex in current_app.custom_extensions:
        try:
            ex.register_dataset(dataset_info.copy())
        except Exception as message:
            logger.warning(message)

    # this is double bookkeeping, next to delegating dataset registration to
    # the search plugin, we also store metadata in an sql table
    register_dataset_admin_metadata(dataset_info)

    return dataset_info["uri"]


def delete_dataset(uri):
    """Delete a dataset in the lookup server. Idempotent.

    :param uri: URI of dataset entry to remove from dserver.
    :returns: URI of successfully removed dataset entry.

    :raises ValidationError: if deletion fails within dserver core, or within search and retrieve plugin."""

    # On the core search and retrieve plugins, we are strict. We expect them
    # to raise ValidationError on failure, we log those, and reraise
    try:
        if hasattr(current_app.search, "delete_dataset"):
            current_app.search.delete_dataset(uri)
        else:
            logger.warning("Search plugin has no method 'delete_dataset'")
            logger.warning("Deletion of dataset entry '%s' will not take effect in search database.'", uri)
    except ValidationError as message:
        # Instead of reporting the error with the logging module, we will want
        # to do some bookkeeping on registration errors per URI in the
        # core SQL db
        logger.error(message)
        raise

    try:
        if hasattr(current_app.retrieve, "delete_dataset"):
            current_app.retrieve.delete_dataset(uri)
        else:
            logger.warning("Retrieve plugin has no method 'delete_dataset'")
            logger.warning("Deletion of dataset entry '%s' will not take effect in retrieve database.'", uri)
    except ValidationError as message:
        logger.error(message)
        raise

    # On any other optional extension, we want to be lenient. We still
    # want to keep track of any error, but the registration should not fail.
    for ex in current_app.custom_extensions:
        try:
            ex.delete_dataset(uri)
        except Exception as message:
            logger.warning(message)

    # this is double bookkeeping, next to delegating dataset registration to
    # the search plugin, we also store metadata in an sql table
    delete_dataset_admin_metadata(uri)

    return uri

#############################################################################
# Dataset information retrieval helper functions
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


#############################################################################
# Retrieve plugin interface
#############################################################################


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


def get_tags_from_uri_by_user(username, uri):
    """Return tags.

    :param username: username
    :param uri: dataset URI
    :returns: dataset tags
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

    return current_app.retrieve.get_tags(uri)


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
