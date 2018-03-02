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

    from app import app
    tmp_db_name = random_string()
    client = app.config["mongo_client"]
    db = client[tmp_db_name]
    collection = db["datasets"]
    app.config["mongo_db"] = db
    app.config["mongo_collection"] = collection

    @request.addfinalizer
    def teardown():
        app.config["mongo_client"].drop_database(tmp_db_name)

    return app.test_client()
