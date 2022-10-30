"""Tests for utils_search.py that don't depend on code in dtool-lookup-server.

For the future when the functionality of utils_search is split into a separate
python package.
"""

import random
import string
import shutil
import tempfile

from contextlib import contextmanager

import pytest

from pymongo import MongoClient

from dtoolcore import DataSetCreator, DataSet

from dtool_lookup_server.utils import generate_dataset_info

# Things tested in this module
from dtool_lookup_server.utils_search import MongoSearch
from dtool_lookup_server.utils_search import _dict_to_mongo_query


MONGO_URI = "mongodb://localhost:27017"


def random_string(
    size=9,
    prefix="test_dtool_lookup_server_mongo_search",
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

def test_lookup_uris(tmp_mongo_db):  # NOQA

    ds_info_1 = create_dataset_info(
        "s3://store1",
        "apple-gala",
        "---\ndescription: gala apples",
        ["barrel1", "barrel2"],
        ["red", "yellow"],
        {"type": "fruit"},
        "farmer"
    )
    ds_info_2 = update_base_uri(ds_info_1.copy(), "s3://store2")
    uuid = ds_info_1["uuid"]

    both_base_uris = ["s3://store1", "s3://store2"]
    only_store2 = ["s3://store2"]

    mongo_search = MongoSearch()
    app = _MockApp()
    app.config = {
        "SEARCH_MONGO_URI": MONGO_URI,
        "SEARCH_MONGO_DB": tmp_mongo_db,
        "SEARCH_MONGO_COLLECTION": "datasets"
    }
    mongo_search.init_app(app)

    # Should be empty. Nothing registered yet.
    assert mongo_search.lookup_uris(uuid, both_base_uris) == []

    # Register a dataset.
    mongo_search.register_dataset(ds_info_1)
    assert mongo_search.lookup_uris(uuid, both_base_uris) == [
        {
            "base_uri": ds_info_1["base_uri"],
            "name": ds_info_1["name"],
            "uri": ds_info_1["uri"],
            "uuid": ds_info_1["uuid"]
            }
    ]

    # Register the same dataset in different base URI
    mongo_search.register_dataset(ds_info_2)
    assert len(mongo_search.lookup_uris(uuid, both_base_uris)) == 2  # NOQA

    # Make sure only the dataset from store2 is retrievd if limited
    # that base URI.
    assert mongo_search.lookup_uris(uuid, only_store2) == [
        {
            "base_uri": ds_info_2["base_uri"],
            "name": ds_info_2["name"],
            "uri": ds_info_2["uri"],
            "uuid": ds_info_2["uuid"]
            }
    ]

    # Make sure nothing is returned if there are no base URIs.
    assert len(mongo_search.lookup_uris(uuid, [])) == 0  # NOQA


def test_register_basic(tmp_mongo_db):  # NOQA

    ds_info = create_dataset_info(
        base_uri="s3://store",
        name="apple-gala",
        readme="---\ndescription: gala apples",
        items_content=["barrel1", "barrel2"],
        tags=["red", "yellow"],
        annotations={"type": "fruit"},
        creator="farmer"
    )

    mongo_search = MongoSearch()
    app = _MockApp()
    app.config = {
        "SEARCH_MONGO_URI": MONGO_URI,
        "SEARCH_MONGO_DB": tmp_mongo_db,
        "SEARCH_MONGO_COLLECTION": "datasets"
    }
    mongo_search.init_app(app)

    # Should be empty. Nothing registered yet.
    assert len(mongo_search.search({"base_uris": ["s3://store"]})) == 0

    # Register a dataset.
    mongo_search.register_dataset(ds_info)
    assert len(mongo_search.search({"base_uris": ["s3://store"]})) == 1

    # Register the same dataset again. Shoud not result in a duplicate record.
    mongo_search.register_dataset(ds_info.copy())
    assert len(mongo_search.search({"base_uris": ["s3://store"]})) == 1


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

    mongo_search = MongoSearch()
    app = _MockApp()
    app.config = {
        "SEARCH_MONGO_URI": MONGO_URI,
        "SEARCH_MONGO_DB": tmp_mongo_db,
        "SEARCH_MONGO_COLLECTION": "datasets"
    }
    mongo_search.init_app(app)

    with pytest.raises(ValidationError):
        mongo_search.register_dataset(ds_info)


def test_search_free_text(tmp_mongo_db):

    mongo_search = MongoSearch()
    app = _MockApp()
    app.config = {
        "SEARCH_MONGO_URI": MONGO_URI,
        "SEARCH_MONGO_DB": tmp_mongo_db,
        "SEARCH_MONGO_COLLECTION": "datasets"
    }
    mongo_search.init_app(app)

    # Add datasets.
    mongo_search.register_dataset(
        create_dataset_info(
            base_uri="s3://farmshop",
            name="farmshop-apples",
            readme="---\ndescription: apples",
            items_content=["barrel1", "barrel2"],
            tags=["red", "yellow", "healthy"],
            annotations={"type": "fruit"},
            creator="farmer"
        )
    )
    mongo_search.register_dataset(
        create_dataset_info(
            base_uri="s3://farmshop",
            name="farmshop-carrots",
            readme="---\ndescription: carrots for good eyesight",
            items_content=["tray1", "tray2"],
            tags=["orange", "healthy"],
            annotations={"type": "vegetable"},
            creator="farmerson"
        )
    )
    mongo_search.register_dataset(
        create_dataset_info(
            base_uri="s3://supermarket",
            name="supermarket-apples",
            readme="---\ndescription: apples",
            items_content=["tray1", "tray2", "tray3"],
            tags=["red", "yellow", "healthy"],
            annotations={"type": "fruit"},
            creator="farmer"
        )
    )

    # Define base URIs for query.
    only_farmshop = ["s3://farmshop"]
    only_supermarket = ["s3://supermarket"]
    both_shops = ["s3://farmshop", "s3://supermarket"]

    # Test the basis of authorization.
    assert len(mongo_search.search({"base_uris": only_farmshop})) == 2
    assert len(mongo_search.search({"base_uris": only_supermarket})) == 1
    assert len(mongo_search.search({"base_uris": both_shops})) == 3

    # Test negative search.
    query = {"base_uris": both_shops, "free_text": "dontexist"}
    assert len(mongo_search.search(query)) == 0

    # Test free text admin metadata.
    query = {"base_uris": both_shops, "free_text": "farmer"}
    assert len(mongo_search.search(query)) == 2
    query = {"base_uris": both_shops, "free_text": "farmerson"}
    assert len(mongo_search.search(query)) == 1
    query = {"base_uris": only_supermarket, "free_text": "farmerson"}
    assert len(mongo_search.search(query)) == 0

    # Test free text readme.
    query = {"base_uris": both_shops, "free_text": "eyesight"}
    assert len(mongo_search.search(query)) == 1
    query = {"base_uris": only_farmshop, "free_text": "eyesight"}
    assert len(mongo_search.search(query)) == 1
    query = {"base_uris": only_supermarket, "free_text": "eyesight"}
    assert len(mongo_search.search(query)) == 0

    # Test free text item content.
    query = {"base_uris": both_shops, "free_text": "tray2"}
    assert len(mongo_search.search(query)) == 2
    query = {"base_uris": both_shops, "free_text": "tray3"}
    assert len(mongo_search.search(query)) == 1
    query = {"base_uris": only_farmshop, "free_text": "tray3"}
    assert len(mongo_search.search(query)) == 0

    # Test free text tags.
    query = {"base_uris": both_shops, "free_text": "red"}
    assert len(mongo_search.search(query)) == 2
    query = {"base_uris": both_shops, "free_text": "orange"}
    assert len(mongo_search.search(query)) == 1
    query = {"base_uris": only_supermarket, "free_text": "orange"}
    assert len(mongo_search.search(query)) == 0

    # Test free text annotations.
    query = {"base_uris": both_shops, "free_text": "fruit"}
    assert len(mongo_search.search(query)) == 2
    query = {"base_uris": both_shops, "free_text": "vegetable"}
    assert len(mongo_search.search(query)) == 1
    query = {"base_uris": only_supermarket, "free_text": "vegetable"}
    assert len(mongo_search.search(query)) == 0

    # Test tags.
    query = {"base_uris": both_shops, "tags": ["healthy"]}
    assert len(mongo_search.search(query)) == 3
    query = {"base_uris": both_shops, "tags": ["healthy", "orange"]}
    assert len(mongo_search.search(query)) == 1
    query = {"base_uris": only_supermarket, "tags": ["healthy", "orange"]}
    assert len(mongo_search.search(query)) == 0

    # Test creator usernames.
    query = {"base_uris": both_shops, "creator_usernames": ["farmer"]}
    assert len(mongo_search.search(query)) == 2
    query = {"base_uris": both_shops, "creator_usernames": ["farmer", "farmerson"]}  # NOQA
    assert len(mongo_search.search(query)) == 3
    query = {"base_uris": only_supermarket, "creator_usernames": ["farmerson"]}
    assert len(mongo_search.search(query)) == 0

    # Test uuid (need to get the uuid first).
    query = {"base_uris": both_shops, "free_text": "eyesight"}
    hits = mongo_search.search(query)
    uuid = hits[0]["uuid"]
    query = {"base_uris": both_shops, "uuids": [uuid]}
    assert len(mongo_search.search(query)) == 1
    query = {"base_uris": only_supermarket, "uuids": [uuid]}
    assert len(mongo_search.search(query)) == 0


##############################################################################
# Test the _dict_to_mongo_query helper function.
##############################################################################

def test_empty_dict():
    """An empty dict should return query for all datasets."""
    assert _dict_to_mongo_query({}) == {}


def test_free_text():
    """Should return {"$text": {"$search": "free_text_here"}}"""
    query = dict(free_text="free_text_here")
    expected_mongo_query = {"$text": {"$search": "free_text_here"}}
    assert _dict_to_mongo_query(query) == expected_mongo_query


def test_creator_usernames():
    # Test single creator username.
    query = dict(creator_usernames=["grumpy"])
    expected_mongo_query = {"creator_username": "grumpy"}
    assert _dict_to_mongo_query(query) == expected_mongo_query

    # Test multiple creator usernames.
    query = dict(creator_usernames=["grumpy", "dopey"])
    expected_mongo_query = {"$or": [
        {"creator_username": "grumpy"},
        {"creator_username": "dopey"}
    ]}
    assert _dict_to_mongo_query(query) == expected_mongo_query

    # Test empty list.
    query = dict(creator_usernames=[])
    assert _dict_to_mongo_query(query) == {}


def test_base_uris():
    # Test single base URI.
    query = dict(base_uris=["s3://snow-white"])
    expected_mongo_query = {"base_uri": "s3://snow-white"}
    assert _dict_to_mongo_query(query) == expected_mongo_query

    # Test multiple base URIs.
    query = dict(base_uris=["s3://snow-white", "s3://mr-men"])
    expected_mongo_query = {"$or": [
        {"base_uri": "s3://snow-white"},
        {"base_uri": "s3://mr-men"}
    ]}
    assert _dict_to_mongo_query(query) == expected_mongo_query


def test_tags():
    # Test single tag.
    query = dict(tags=["evil"])
    expected_mongo_query = {"tags": "evil"}
    assert _dict_to_mongo_query(query) == expected_mongo_query

    # Test multiple tags.
    query = dict(tags=["evil", "good"])
    expected_mongo_query = {"tags": {"$all": ["evil", "good"]}}
    assert _dict_to_mongo_query(query) == expected_mongo_query

    # Test empty list.
    query = dict(tags=[])
    assert _dict_to_mongo_query(query) == {}


def test_combinations():
    query = dict(
        free_text="apple",
        base_uris=["s3://snow-white"],
        creator_usernames=["grumpy", "dopey"],
        tags=["good", "evil"]
    )
    expected_mongo_query = {}
    expected_mongo_query = {
        "$and": [
            {"$text": {"$search": "apple"}},
            {"$or": [
                {"creator_username": "grumpy"},
                {"creator_username": "dopey"}
            ]
            },
            {"base_uri": "s3://snow-white"},
            {"tags": {"$all": ["good", "evil"]}}
        ]
    }
    assert _dict_to_mongo_query(query) == expected_mongo_query