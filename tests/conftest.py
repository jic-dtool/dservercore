import random
import string
import os
import sys
import tempfile
import shutil

from contextlib import contextmanager

import pytest

# Pytest does not add the working directory to the path so we do it here.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..")
sys.path.insert(0, _ROOT)

JWT_PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8LrEp0Q6l1WPsY32uOPqEjaisQScnzO/XvlhQTzj5w+hFObjiNgIaHRceYh3hZZwsRsHIkCxOY0JgUPeFP9IVXso0VptIjCPRF5yrV/+dF1rtl4eyYj/XOBvSDzbQQwqdjhHffw0TXW0f/yjGGJCYM+tw/9dmj9VilAMNTx1H76uPKUo4M3vLBQLo2tj7z1jlh4Jlw5hKBRcWQWbpWP95p71Db6gSpqReDYbx57BW19APMVketUYsXfXTztM/HWz35J9HDya3ID0Dl+pE22Wo8SZo2+ULKu/4OYVcD8DjF15WwXrcuFDypX132j+LUWOVWxCs5hdMybSDwF3ZhVBH ec2-user@ip-172-31-41-191.eu-west-1.compute.internal"  # NOQA


def random_string(
    size=9,
    prefix="test_",
    chars=string.ascii_uppercase + string.ascii_lowercase + string.digits
):
    return prefix + ''.join(random.choice(chars) for _ in range(size))


@contextmanager
def tmp_env_var(key, value):
    os.environ[key] = value
    yield
    del os.environ[key]


@contextmanager
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


@pytest.fixture
def snowwhite_token():
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYyMTEwMDgzMywianRpIjoiNmE3Yjk5NDYtNzU5My00OGNmLTg2NmUtMWJjZGIzNjYxNTVjIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InNub3ctd2hpdGUiLCJuYmYiOjE2MjExMDA4MzN9.gXdQpGnHDdOHTMG5OKJwNe8JoJU7JSGYooU5d8AxA_Vs8StKBBRKZJ6C6zS8SovIgcDEYGP12V25ZOF_fa42GuQErKqfwJ_RTLB8nHvfEJule9dl_4z-8-5dZigm3ieiYPpX8MktHq4FQ5vdQ36igWyTO5sK4X4GSvZjG6BRphM52Rb9J2aclO1lxuD_HV_c_rtIXI-SLxH3O6LLts8RdjqLJZBNhAPD4qjAbg_IDi8B0rh_I0R42Ou6J_Sj2s5sL97FEY5Jile0MSvBH7OGmXjlcvYneFpPLnfLwhsYUrzqYB-fdhH9AZVBwzs3jT4HGeL0bO0aBJ9sJ8YRU7sjTg"  # NOQA


@pytest.fixture
def grumpy_token():
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYyMTEwMTY0NywianRpIjoiYWFmMTc3NTQtNzc4Mi00ODAzLThlZDItODZhYmI0ZDVhYThlIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImdydW1weSIsIm5iZiI6MTYyMTEwMTY0N30.tvYTnOflEGjPM1AmDMQxE-2CAa7Je3uhq5DEQutUUGyuMHyT7phsam8l0aHGQjlCZb2X98Gs9QeQ5rXwxP5y8oteQzk26QbunW3Jpg46E1PheESURqOScLgyyiKa6aHtztb5aa5VxK2LgFB13JrQZ03GJpuDPQj7q1Lbu2Cn0JjX3YXRuF14ZkZk8ZrybnKsJ3RLKup_SUDeDx20hJFYBbnyd8jZSd5xV9eQfSrMHFhDBAnV9c8gzMXKnNR5OtVLyFWVrOB4OsP3Woy2eyXmM9G3Qljft6j_jtYcra7-7BnvIZE8JSLcTT0cH563KISFNqMxmkrWqhZaHRCRRhwsPg"  # NOQA


@pytest.fixture
def dopey_token():
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYyMTEwMTY5NCwianRpIjoiZjNlOTFmNjQtZTIzZi00MWRkLThhOTAtMWUzYzkzMDlmYTM0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImRvcGV5IiwibmJmIjoxNjIxMTAxNjk0fQ.KJHiQN3MNGsfRQ_pGU0AGNSP-7-PR3oWvxUxjqtY23FPcrH3dJ3MTSVvD1kWiiEOkE-3kbq9KOg8g4OhpifBM44DbA-R5Xjuk_99Grc6TnPQMaB7W5s1k8JCs20wTW4gAM4t1ANixVQT0IW6T0OF_WeotWp-RaOkzYlMAp3KNotCNvlbj-fS-d3NEDucNjbHG_p9DgbOVLxD1jM-7GykMpLNvVeI5KZkgjvtxXvQt2sU_Dnm-J15TmknUaO6pLF--OA8AM8rZDf4p-QISsOu6uQEbxo9XSU_OHe7pzNebge54v3hd0vj5nAVqLg73myUHqOximaaObQRXk7ZOqjE4g"  # NOQA


@pytest.fixture
def sleepy_token():
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYyMTEwMTcxOCwianRpIjoiMDM2YmNmZTktODg5OC00Nzg0LWIwYWQtZTRkOTczN2JjZjgxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InNsZWVweSIsIm5iZiI6MTYyMTEwMTcxOH0.OoHNM5l_p8n2OKz-IEondgHzUhHwXmPY0rWnXrto9WSkHEGOAL6Yqc37dancRUIzvvG2l_oK88O0eHJEFMPT0M0F-18wvCQ9wdQfiAUSiagFw4o_sUomHXu0xWjDFZ-gClUW-85qZiyKjx8gYvCYod1rehBy1B52kZ6DAd2tzQfwzI8ncgsjdsqGcOotkLisidGrqRA2jXqeJjPrwNQlHNl4OH7n7pxzzMb4_spyWEG12pjYZwa77oMDim_RjQpmo8RnNOEgenN9fGnBN3myluKY8AV7ZCat5vORzrKARWOj_-EQr6c6-9ZrxLWArEVkecB-WG6f5U8KmnUsrPq6Cg"  # NOQA


@pytest.fixture
def noone_token():
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYyMTEwMTc1MywianRpIjoiZWVlODQ1MmMtZGJkYi00Njk1LWFmYWItNDhmZTQ2ZDNlYzE4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Im5vb25lIiwibmJmIjoxNjIxMTAxNzUzfQ.HFfZFesk55Wi6ucUyjs3XR80giJhIvuK-9mrwJ0X0pvKqRGaa6kfPssZgO9LwrMsjRNClQVLdaHr12YTuMmPWAXj7glLvQeaGP60tfGhDacHJxIEQT1PyVdynGz66y4o13Gq32MY5zMXM4cFCy6-n0x6T-Gzrw5lJyn_wXGFeUE2rms19RZt4UrDLUXeKZlGUPyeMd34j23Io5IegrL4U5LLHvmP8IM9xZROcruJ87FLSZxHIdjg36YZ8oyTt7L8W-26fR6Ts_asyEpm0nOo8N1lszNPkx87f7Ckwyqoyom33nUIJUapDPR0LqYNd8bH_rp37Ed31zlAIU0L-hAipA"  # NOQA


@pytest.fixture
def tmp_app(request):

    from flask import current_app
    from dservercore import create_app, sql_db

    tmp_mongo_db_name = random_string()

    config = {
        "CONFIG_SECRETS_TO_OBFUSCATE": [],
        "API_TITLE": 'dservercore API',
        "API_VERSION": 'v1',
        "OPENAPI_VERSION": '3.0.2',
        "API_SPEC_OPTIONS": {
            'x-internal-id': '2',
            'security': [{"bearerAuth": []}],
            'components': {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        },
        "SECRET_KEY": "secret",
        "FLASK_ENV": "development",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "RETRIEVE_MONGO_URI": "mongodb://localhost:27017/",
        "RETRIEVE_MONGO_DB": tmp_mongo_db_name,
        "RETRIEVE_MONGO_COLLECTION": "datasets",
        "SEARCH_MONGO_URI": "mongodb://localhost:27017/",
        "SEARCH_MONGO_DB": tmp_mongo_db_name,
        "SEARCH_MONGO_COLLECTION": "datasets",
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
        current_app.retrieve.client.drop_database(tmp_mongo_db_name)
        current_app.search.client.drop_database(tmp_mongo_db_name)
        sql_db.session.remove()

    return app


@pytest.fixture
def tmp_app_client(tmp_app):
    return tmp_app.test_client()


@pytest.fixture
def tmp_app_with_users(request):

    from flask import current_app

    from dservercore import create_app, sql_db
    from dservercore.utils import (
        register_users,
        register_base_uri,
        register_permissions,
    )

    tmp_mongo_db_name = random_string()

    config = {
        "CONFIG_SECRETS_TO_OBFUSCATE": [],
        "API_TITLE": 'dservercore API',
        "API_VERSION": 'v1',
        "OPENAPI_VERSION": '3.0.2',
        "SECRET_KEY": "secret",
        "FLASK_ENV": "development",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "RETRIEVE_MONGO_URI": "mongodb://localhost:27017/",
        "RETRIEVE_MONGO_DB": tmp_mongo_db_name,
        "RETRIEVE_MONGO_COLLECTION": "datasets",
        "SEARCH_MONGO_URI": "mongodb://localhost:27017/",
        "SEARCH_MONGO_DB": tmp_mongo_db_name,
        "SEARCH_MONGO_COLLECTION": "datasets",
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
        "users_with_search_permissions": ["grumpy", "sleepy"],
        "users_with_register_permissions": ["grumpy"]
    }
    register_permissions(base_uri, permissions)

    @request.addfinalizer
    def teardown():
        current_app.retrieve.client.drop_database(tmp_mongo_db_name)
        current_app.search.client.drop_database(tmp_mongo_db_name)
        sql_db.session.remove()

    return app


@pytest.fixture
def tmp_app_with_users_client(tmp_app_with_users):
    return tmp_app_with_users.test_client()


@pytest.fixture
def tmp_app_with_data(request):

    from flask import current_app

    from dservercore import create_app, sql_db
    from dservercore.utils import (
        register_users,
        register_base_uri,
        register_dataset,
        register_permissions,
    )

    tmp_mongo_db_name = random_string()

    config = {
        "API_TITLE": 'dservercore API',
        "API_VERSION": 'v1',
        "OPENAPI_VERSION": '3.0.2',
        "FLASK_ENV": "development",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "RETRIEVE_MONGO_URI": "mongodb://localhost:27017/",
        "RETRIEVE_MONGO_DB": tmp_mongo_db_name,
        "RETRIEVE_MONGO_COLLECTION": "datasets",
        "SEARCH_MONGO_URI": "mongodb://localhost:27017/",
        "SEARCH_MONGO_DB": tmp_mongo_db_name,
        "SEARCH_MONGO_COLLECTION": "datasets",
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
            "users_with_search_permissions": [username],
            "users_with_register_permissions": [username]
        }
        register_permissions(base_uri, permissions)

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
            "readme": "---\ndescripton: apples from queen",
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
            "size_in_bytes": 5741810,
            "number_of_items": 1,
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
        "readme": "---\ndescripton: oranges from queen",
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "creator_username": "queen",
        "frozen_at": 1536238185.881941,
        "annotations": {"type": "fruit", "only_here": "crazystuff"},
        "tags": ["good", "fruit"],
        "size_in_bytes": 0,
        "number_of_items": 0,
    }
    register_dataset(dataset_info)

    @request.addfinalizer
    def teardown():
        current_app.retrieve.client.drop_database(tmp_mongo_db_name)
        current_app.search.client.drop_database(tmp_mongo_db_name)
        sql_db.session.remove()

    return app


@pytest.fixture
def tmp_app_with_data_client(tmp_app_with_data):
    return tmp_app_with_data.test_client()


@pytest.fixture
def tmp_cli_runner(request):

    from flask import current_app

    from dservercore import create_app, sql_db

    tmp_mongo_db_name = random_string()

    config = {
        "API_TITLE": 'dservercore API',
        "API_VERSION": 'v1',
        "OPENAPI_VERSION": '3.0.2',
        "FLASK_ENV": "development",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "RETRIEVE_MONGO_URI": "mongodb://localhost:27017/",
        "RETRIEVE_MONGO_DB": tmp_mongo_db_name,
        "RETRIEVE_MONGO_COLLECTION": "datasets",
        "SEARCH_MONGO_URI": "mongodb://localhost:27017/",
        "SEARCH_MONGO_DB": tmp_mongo_db_name,
        "SEARCH_MONGO_COLLECTION": "datasets",
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
        current_app.retrieve.client.drop_database(tmp_mongo_db_name)
        current_app.search.client.drop_database(tmp_mongo_db_name)
        sql_db.session.remove()

    return app.test_cli_runner()
