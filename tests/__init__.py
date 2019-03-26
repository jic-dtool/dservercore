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
    }
    register_dataset(dataset_info)

    @request.addfinalizer
    def teardown():
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
