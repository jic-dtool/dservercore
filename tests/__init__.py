import random
import string
import os
import sys

import pytest

# Pytest does not add the working directory to the path so we do it here.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..")
sys.path.insert(0, _ROOT)


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

    return app.test_client()


@pytest.fixture
def tmp_app_with_data(request):

    from dtool_lookup_server import create_app, mongo, sql_db
    from dtool_lookup_server.utils import (
        register_users,
        register_base_uri,
        register_dataset_admin_metadata,
        update_permissions,
    )

    tmp_mongo_db_name = random_string()

    jwt_public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDV+7UTCb5JMX/GIY3g6kus84K5ko08nKbZcPgtRbTOkdNLFDcfotefNi+Y3bDEwMydXyc7uBmLkl9hyjBwTdCj6zAJ4VhLZ5wN0qg1cmg4Wkm6EUFgBHf7NY6V5M+v6XyZFinmzoe+J5llTH5xXLkieNMNtSDPUZWtRyhT9bwNSzYzBYZ13L1/yJJVUnb8mUmC2RG5ZqT8DZ+R/Y0Z35qACNmVqFTbSwFm3IoW2XcMXZawAKGoj0e9z6Eo6KZIRmVEFOfoeokz92zhS4b+j0+OJfmknpLYLHEyHswOnyFXFeNH1AHkGjDcAZwfr5ZMKpsy9XXlGiO2kFhK7RQ1ITvF olssont@n95996.nbi.ac.uk"  # NOQA

    config = {
        "FLASK_ENV": "development",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "MONGO_URI": "mongodb://localhost:27017/{}".format(tmp_mongo_db_name),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "dev",
        "JWT_PUBLIC_KEY": jwt_public_key
    }

    app = create_app(config)

    # Ensure the sql database has been put into the context.
    app.app_context().push()

    # Populate the database.
    sql_db.Model.metadata.create_all(sql_db.engine)

    # Add some data to the database.
    base_uri = "s3://snow-white"
    register_base_uri(base_uri)

    username = "grumpy"
    register_users([dict(username=username), dict(username="sleepy")])

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    admin_metadata = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "bad-apples"
    }
    register_dataset_admin_metadata(admin_metadata)

    permissions = {
        "base_uri": base_uri,
        "users_with_search_permissions": [username],
        "users_with_register_permissions": []
    }
    update_permissions(permissions)

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
