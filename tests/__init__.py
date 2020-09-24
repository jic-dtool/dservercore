import logging
import random
import string
import os
import sys

import pytest

# Pytest does not add the working directory to the path so we do it here.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..")
sys.path.insert(0, _ROOT)

JWT_PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDV+7UTCb5JMX/GIY3g6kus84K5ko08nKbZcPgtRbTOkdNLFDcfotefNi+Y3bDEwMydXyc7uBmLkl9hyjBwTdCj6zAJ4VhLZ5wN0qg1cmg4Wkm6EUFgBHf7NY6V5M+v6XyZFinmzoe+J5llTH5xXLkieNMNtSDPUZWtRyhT9bwNSzYzBYZ13L1/yJJVUnb8mUmC2RG5ZqT8DZ+R/Y0Z35qACNmVqFTbSwFm3IoW2XcMXZawAKGoj0e9z6Eo6KZIRmVEFOfoeokz92zhS4b+j0+OJfmknpLYLHEyHswOnyFXFeNH1AHkGjDcAZwfr5ZMKpsy9XXlGiO2kFhK7RQ1ITvF olssont@n95996.nbi.ac.uk"  # NOQA

TESTING_FAMILY = {
    'grandfather': {
        'uuid': "a2218059-5bd0-4690-b090-062faf08e040"
    },
    'grandmother': {
        'uuid': "a2218059-5bd0-4690-b090-062faf08e041",
        'derived_from': ["a2218059-5bd0-4690-b090-062faf08e039"]  # not in set
    },
    'mother': {
        'uuid': "a2218059-5bd0-4690-b090-062faf08e042",
        'derived_from': ['grandfather', 'grandmother'],
    },
    'father': {
        'uuid': "a2218059-5bd0-4690-b090-062faf08e043",
        'derived_from': ['unknown'],  # invalid
    },
    'brother': {
        'uuid': "a2218059-5bd0-4690-b090-062faf08e044",
        'derived_from': ['mother', 'father'],
    },
    'sister': {
        'uuid': "a2218059-5bd0-4690-b090-062faf08e045",
        'derived_from': ['mother', 'father'],
    },
    'stepsister': {
        'uuid': "a2218059-5bd0-4690-b090-062faf08e046",
        'derived_from': ['mother', 'ex-husband'],
    },
    'ex-husband': {
        'uuid': "a2218059-5bd0-4690-b090-062faf08e047",
        'derived_from': ['unknown'],  # invalid
    },
    'friend': {
        'uuid': "a2218059-5bd0-4690-b090-062faf08e048",
        "verived_from": ["friend's mother, friend's father"]
    }
}

BASE_URI = "s3://snow-white"


def family_datasets(base_uri=BASE_URI):
    return [
        {
            "base_uri": base_uri,
            "type": "dataset",
            "uuid": family_tree_entry['uuid'],
            "uri": "{}/{}".format(base_uri, family_tree_entry['uuid']),
            "name": role,
            "readme": {
                "derived_from": [
                    {"uuid": TESTING_FAMILY[parent]["uuid"] if parent in TESTING_FAMILY else parent}
                    for parent in family_tree_entry["derived_from"]
                ]
            } if "derived_from" in family_tree_entry else {},
            "creator_username": "god",
            "frozen_at": 1536238185.881941,
            "manifest": {
                "dtoolcore_version": "3.7.0",
                "hash_function": "md5sum_hexdigest",
                "items": {}
            },
            "annotations": {"type": "member of the family"},
            "tags": ["person"],
        } for role, family_tree_entry in TESTING_FAMILY.items()
    ]


def compare_nested(A, B):
    """Compare nested dicts and lists."""
    if isinstance(A, list) and isinstance(B, list):
        for a, b in zip(A, B):
            if not compare_nested(a, b):
                return False
        return True

    if isinstance(A, dict) and isinstance(B, dict):
        if set(A.keys()) == set(B.keys()):
            for k in A.keys():
                if not compare_nested(A[k], B[k]):
                    return False
            return True
        else:
            return False
    return A == B


def comparison_marker_from_obj(obj):
    """Mark all nested objects for comparison."""
    if isinstance(obj, list):
        marker = []
        for elem in obj:
            marker.append(comparison_marker_from_obj(elem))
    elif isinstance(obj, dict):
        marker = {}
        for k, v in obj.items():
            marker[k] = comparison_marker_from_obj(v)
    else:
        marker = True
    return marker


def compare_marked_nested(A, B, marker):
    """Compare source and target partially, as marked by marker."""
    logger = logging.getLogger(__name__)
    if isinstance(marker, dict):
        for k, v in marker.items():
            if k not in A:
                logger.error("{} not in A '{}'.".format(k, A))
                return False
            if k not in B:
                logger.error("{} not in B '{}'.".format(k, A))
                return False

            logger.debug("Descending into sub-tree '{}' of '{}'.".format(
                A[k], A))
            # descend
            if not compare_marked_nested(A[k], B[k], v):
                return False  # one failed comparison suffices
    # A, B and marker must have same length:
    elif isinstance(marker, list):
        if len(A) != len(B) or len(marker) != len(B):
            logger.debug("A, B, and marker don't have equal length at "
                         "'{}', '{}', '{}'.".format(A, B, marker))
            return False
        logger.debug("Branching into element wise sub-trees of '{}'.".format(
            A))
        for s, t, m in zip(A, B, marker):
            if not compare_marked_nested(s, t, m):
                return False  # one failed comparison suffices
    else:  # arrived at leaf, comparison desired?
        if marker:  # yes
            logger.debug("Comparing '{}' == '{}' -> {}.".format(
                A, B, A == B))
            return A == B

    # comparison either not desired or successfull for all elements
    return True


def random_string(
    size=9,
    prefix="test_",
    chars=string.ascii_uppercase + string.ascii_lowercase + string.digits
):
    return prefix + ''.join(random.choice(chars) for _ in range(size))


@pytest.fixture
def tmp_app(request):

    from dtool_lookup_server import create_app, mongo, sql_db

    tmp_mongo_db_name = random_string()

    config = {
        "SECRET_KEY": "secret",
        "FLASK_ENV": "development",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "MONGO_URI": "mongodb://localhost:27017/{}".format(tmp_mongo_db_name),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_ALGORITHM": "RS256",
        "JWT_PUBLIC_KEY": JWT_PUBLIC_KEY,
        "JWT_TOKEN_LOCATION": "headers",
        "JWT_HEADER_NAME": "Authorization",
        "JWT_HEADER_TYPE": "Bearer",
    }

    app = create_app(config)

    # Ensure the sql database has been put into the context.
    app.app_context().push()

    # Populate the database.
    sql_db.Model.metadata.create_all(sql_db.engine)

    @request.addfinalizer
    def teardown():
        mongo.cx.drop_database(tmp_mongo_db_name)
        sql_db.session.remove()

    return app.test_client()


@pytest.fixture
def tmp_app_with_users(request):

    from dtool_lookup_server import create_app, mongo, sql_db
    from dtool_lookup_server.utils import (
        register_users,
        register_base_uri,
        update_permissions,
    )

    tmp_mongo_db_name = random_string()

    config = {
        "SECRET_KEY": "secret",
        "FLASK_ENV": "development",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "MONGO_URI": "mongodb://localhost:27017/{}".format(tmp_mongo_db_name),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_ALGORITHM": "RS256",
        "JWT_PUBLIC_KEY": JWT_PUBLIC_KEY,
        "JWT_TOKEN_LOCATION": "headers",
        "JWT_HEADER_NAME": "Authorization",
        "JWT_HEADER_TYPE": "Bearer",
    }

    app = create_app(config)

    # Ensure the sql database has been put into the context.
    app.app_context().push()

    # Populate the database.
    sql_db.Model.metadata.create_all(sql_db.engine)

    # Register some users.
    register_users([
        dict(username="snow-white", is_admin=True),
        dict(username="grumpy"),
        dict(username="sleepy"),
    ])

    base_uri = "s3://snow-white"
    register_base_uri(base_uri)

    permissions = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy"],
        "users_with_register_permissions": ["grumpy"]
    }
    update_permissions(permissions)

    @request.addfinalizer
    def teardown():
        mongo.cx.drop_database(tmp_mongo_db_name)
        sql_db.session.remove()

    return app.test_client()


@pytest.fixture
def tmp_app_with_data(request):

    from dtool_lookup_server import create_app, mongo, sql_db
    from dtool_lookup_server.utils import (
        register_users,
        register_base_uri,
        register_dataset,
        update_permissions,
    )

    tmp_mongo_db_name = random_string()

    config = {
        "FLASK_ENV": "development",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "MONGO_URI": "mongodb://localhost:27017/{}".format(tmp_mongo_db_name),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_ALGORITHM": "RS256",
        "JWT_PUBLIC_KEY": JWT_PUBLIC_KEY,
        "JWT_TOKEN_LOCATION": "headers",
        "JWT_HEADER_NAME": "Authorization",
        "JWT_HEADER_TYPE": "Bearer",
    }

    app = create_app(config)

    # Ensure the sql database has been put into the context.
    app.app_context().push()

    # Populate the database.
    sql_db.Model.metadata.create_all(sql_db.engine)

    # Register some users.
    username = "grumpy"
    register_users([
        dict(username=username),
        dict(username="sleepy"),
        dict(username="snow-white", is_admin=True)
    ])

    # Add base URIs and update permissions
    for base_uri in ["s3://snow-white", "s3://mr-men"]:
        register_base_uri(base_uri)
        permissions = {
            "base_uri": base_uri,
            "users_with_search_permissions": [username],
            "users_with_register_permissions": [username]
        }
        update_permissions(permissions)

    # Add some data to the database.
    for base_uri in ["s3://snow-white", "s3://mr-men"]:
        uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
        uri = "{}/{}".format(base_uri, uuid)
        dataset_info = {
            "base_uri": base_uri,
            "type": "dataset",
            "uuid": uuid,
            "uri": uri,
            "name": "bad-apples",
            "readme": {"descripton": "apples from queen"},
            "manifest": {
                "dtoolcore_version": "3.7.0",
                "hash_function": "md5sum_hexdigest",
                "items": {
                    "e4cc3a7dc281c3d89ed4553293c4b4b110dc9bf3": {
                        "hash": "d89117c9da2cc34586e183017cb14851",
                        "relpath": "U00096.3.rev.1.bt2",
                        "size_in_bytes": 5741810,
                        "utc_timestamp": 1536832115.0
                    }
                }
            },
            "creator_username": "queen",
            "frozen_at": 1536238185.881941,
            "annotations": {"type": "fruit"},
            "tags": ["evil", "fruit"],
        }
        register_dataset(dataset_info)

    base_uri = "s3://snow-white"
    uuid = "a2218059-5bd0-4690-b090-062faf08e046"
    uri = "{}/{}".format(base_uri, uuid)
    dataset_info = {
        "base_uri": base_uri,
        "type": "dataset",
        "uuid": uuid,
        "uri": uri,
        "name": "oranges",
        "readme": {"descripton": "oranges from queen"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "creator_username": "queen",
        "frozen_at": 1536238185.881941,
        "annotations": {"type": "fruit", "only_here": "crazystuff"},
        "tags": ["good", "fruit"],
    }
    register_dataset(dataset_info)

    @request.addfinalizer
    def teardown():
        mongo.cx.drop_database(tmp_mongo_db_name)
        sql_db.session.remove()

    return app.test_client()


@pytest.fixture
def tmp_app_with_data_and_relaxed_security(request, tmp_app_with_data):
    from dtool_lookup_server.config import Config
    Config.QUERY_DICT_VALID_KEYS.append("query")
    Config.ALLOW_DIRECT_AGGREGATION = True

    @request.addfinalizer
    def teardown():
        Config.QUERY_DICT_VALID_KEYS.remove("query")
        Config.ALLOW_DIRECT_AGGREGATION = False

    return tmp_app_with_data


@pytest.fixture
def tmp_app_with_dependent_data(request):
    from dtool_lookup_server.config import Config
    from dtool_lookup_server import create_app, mongo, sql_db
    from dtool_lookup_server.utils import (
        register_users,
        register_base_uri,
        register_dataset,
        update_permissions,
    )

    tmp_mongo_db_name = random_string()

    config = {
        "FLASK_ENV": "development",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "MONGO_URI": "mongodb://localhost:27017/{}".format(tmp_mongo_db_name),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_ALGORITHM": "RS256",
        "JWT_PUBLIC_KEY": JWT_PUBLIC_KEY,
        "JWT_TOKEN_LOCATION": "headers",
        "JWT_HEADER_NAME": "Authorization",
        "JWT_HEADER_TYPE": "Bearer",
    }

    Config.ALLOW_DIRECT_AGGREGATION = True
    Config.ENABLE_DEPENDENCY_VIEW = True

    app = create_app(config)

    # Ensure the sql database has been put into the context.
    app.app_context().push()

    # Populate the database.
    sql_db.Model.metadata.create_all(sql_db.engine)

    # Register some users.
    username = "grumpy"
    register_users([
        dict(username=username),
    ])

    base_uri = "s3://snow-white"
    register_base_uri(base_uri)
    permissions = {
        "base_uri": base_uri,
        "users_with_search_permissions": [username],
        "users_with_register_permissions": [username]
    }
    update_permissions(permissions)

    for dataset_info in family_datasets(base_uri):
        register_dataset(dataset_info)

    @request.addfinalizer
    def teardown():
        Config.ALLOW_DIRECT_AGGREGATION = False
        mongo.cx.drop_database(tmp_mongo_db_name)
        sql_db.session.remove()

    return app.test_client()


@pytest.fixture
def tmp_cli_runner(request):

    from dtool_lookup_server import create_app, mongo, sql_db

    tmp_mongo_db_name = random_string()

    config = {
        "FLASK_ENV": "development",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "MONGO_URI": "mongodb://localhost:27017/{}".format(tmp_mongo_db_name),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "dev"
    }

    app = create_app(config)

    # Ensure the sql database has been put into the context.
    app.app_context().push()

    # Populate the database.
    sql_db.Model.metadata.create_all(sql_db.engine)

    @request.addfinalizer
    def teardown():
        mongo.cx.drop_database(tmp_mongo_db_name)
        sql_db.session.remove()

    return app.test_cli_runner()
