"""Standalone tests for utils_retrieve.py in preparation for extraction into
its own python package."""

from __future__ import annotations
import random
import string
import shutil
import tempfile

from contextlib import contextmanager

import pytest

from pymongo import MongoClient

from dtoolcore import DataSetCreator, DataSet

from dtool_lookup_server.utils import generate_dataset_info

# This tested in this module.
from dtool_lookup_server.utils_retrieve import MongoRetrieve


MONGO_URI = "mongodb://localhost:27017"


def random_string(
    size=9,
    prefix="test_dtool_lookup_server_mongo_retreive",
    chars=string.ascii_uppercase + string.ascii_lowercase + string.digits
):
    return prefix + ''.join(random.choice(chars) for _ in range(size))


@pytest.fixture
def tmp_mongo_db(request):
    tmp_mongo_db_name = random_string()
    client = MongoClient(MONGO_URI)

    @request.addfinalizer
    def teardown():
        client.drop_database(tmp_mongo_db_name)

    return tmp_mongo_db_name


@contextmanager
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


def update_base_uri(ds_info, base_uri):
    ds_uri = base_uri + "/" + ds_info["uuid"]
    ds_info["uri"] = ds_uri
    ds_info["base_uri"] = base_uri
    return ds_info


def create_dataset_info(base_uri, name, readme, items_content, tags, annotations, creator):  # NOQA
    with tmp_dir() as d:
        with DataSetCreator(name, d, readme, creator) as ds_creator:
            for ic in items_content:
                handle = ic + ".txt"
                fpath = ds_creator.prepare_staging_abspath_promise(handle)
                with open(fpath, "w") as fh:
                    fh.write(ic)
            for tag in tags:
                ds_creator.put_tag(tag)
            for key, value in annotations.items():
                ds_creator.put_annotation(key, value)
        dataset = DataSet.from_uri(ds_creator.uri)
        ds_info = generate_dataset_info(dataset, base_uri)

        ds_info = update_base_uri(ds_info, base_uri)

        return ds_info


class _MockApp(object):
    "Class to mock a Flask app to hold a config dict."
    pass
    

##############################################################################
# Here are the tests
##############################################################################

def test_is_subclass_of_abc():
    from dtool_lookup_server import RetrieveABC
    assert issubclass(MongoRetrieve, RetrieveABC)


def test_functional(tmp_mongo_db):  # NOQA

    from dtool_lookup_server import UnknownURIError

    ds_info = create_dataset_info(
        base_uri="s3://store",
        name="apple-gala",
        readme="---\ndescription: gala apples",
        items_content=["barrel1", "barrel2"],
        tags=["red", "yellow"],
        annotations={"type": "fruit"},
        creator="farmer"
    )

    mongo_retreive = MongoRetrieve()
    app = _MockApp()
    app.config = {
        "RETRIEVE_MONGO_URI": MONGO_URI,
        "RETRIEVE_MONGO_DB": tmp_mongo_db,
        "RETRIEVE_MONGO_COLLECTION": "datasets"
    }
    mongo_retreive.init_app(app)

    uri = ds_info["uri"]

    # Nothing registered yet.
    with pytest.raises(UnknownURIError):
        mongo_retreive.get_readme(uri)

    with pytest.raises(UnknownURIError):
        mongo_retreive.get_manifest(uri)

    with pytest.raises(UnknownURIError):
        mongo_retreive.get_annotations(uri)

    # Register a dataset.
    mongo_retreive.register_dataset(ds_info)

    # Now one can retrieve the documents.
    readme = mongo_retreive.get_readme(uri)
    assert readme == ds_info["readme"]

    manifest = mongo_retreive.get_manifest(uri)
    assert manifest == ds_info["manifest"]

    annotations = mongo_retreive.get_annotations(uri)
    assert annotations == ds_info["annotations"]


def test_register_raises_when_metadata_too_large(tmp_mongo_db):  # NOQA

    from dtool_lookup_server import ValidationError

    readme_lines = ["---"]
    for i in range(100000):
        key = "here_is_a_long_key_{}".format(i)
        value = "here_is_a_long_value_{}".format(i) * 10
        readme_lines.append("{}: {}".format(key, value))
    ds_info = create_dataset_info(
        "s3://store",
        "apple-gala",
        "\n".join(readme_lines),
        ["barrel1", "barrel2"],
        ["red", "yellow"],
        {"type": "fruit"},
        "farmer"
    )

    mongo_retreive = MongoRetrieve()
    app = _MockApp()
    app.config = {
        "RETRIEVE_MONGO_URI": MONGO_URI,
        "RETRIEVE_MONGO_DB": tmp_mongo_db,
        "RETRIEVE_MONGO_COLLECTION": "datasets"
    }
    mongo_retreive.init_app(app)

    with pytest.raises(ValidationError):
        mongo_retreive.register_dataset(ds_info)