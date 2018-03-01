import random
import string

import pytest

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
