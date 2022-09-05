"""Test the search utility functions."""

# DONE: copy over all the tests from test_dict_to_mongo_query.py
# DONE: rework and add all search tests from test_dataset_routes.py
# TODO: add tests and functionality for mongo_search.register_dataset()
# TODO: add tests and functionality for mongo_search.lookup_uris()
# TODO: rework test fixture to make it stand alone from dtool-lookup-server (use register_dataset to make it easier to build it up)

import pytest
import pymongo

from . import tmp_app_with_data  # NOQA
from . import tmp_env_var

def test_functional(tmp_app_with_data):  # NOQA

    from dtool_lookup_server.utils_search import MongoSearch
    from dtool_lookup_server.utils import preprocess_query_base_uris


    # For this test we will just rip the MONGO_URI out of the app config.
    mongo_uri = tmp_app_with_data.application.config["MONGO_URI"]

    # For this test we will just rip it out of the MONGO_URI.
    parsed = pymongo.uri_parser.parse_uri(mongo_uri)
    mongo_db = parsed['database']

    # Make sure we get a RuntimeError if the MONGO_URI has not been specified.
    with pytest.raises(RuntimeError):
        MongoSearch()

    with tmp_env_var("MONGO_URI", mongo_uri):

        # Make sure we get a RuntimeError if the MONGO_DB has not been set.
        with pytest.raises(RuntimeError):
            MongoSearch()

        with tmp_env_var("MONGO_DB", mongo_db):

            # Make sure we get a RuntimeError if the MONGO_COLLECTION has not been set.
            with pytest.raises(RuntimeError):
                MongoSearch()

            with tmp_env_var("MONGO_COLLECTION", "datasets"):

                mongo_search = MongoSearch()

                # Get all for grumpy user.
                query = preprocess_query_base_uris("grumpy", {})
                result = mongo_search.search(query)
                assert len(result) == 3

                # Get all for sleep user.
                query = preprocess_query_base_uris("sleepy", {})
                result = mongo_search.search(query)
                assert len(result) == 0

                # Search for apples (in README).
                query = preprocess_query_base_uris(
                    "grumpy",
                    {"free_text": "apple"}
                )
                result = mongo_search.search(query)
                assert len(result) == 2

                # Search for U00096 (in manifest).
                query = preprocess_query_base_uris(
                    "grumpy",
                    {"free_text": "U00096"}
                )
                result = mongo_search.search(query)
                assert len(result) == 2

                # Search for crazystuff (in annotaitons).
                query = preprocess_query_base_uris(
                    "grumpy",
                    {"free_text": "crazystuff"}
                )
                result = mongo_search.search(query)
                assert len(result) == 1

                # Tag test 1.
                query = preprocess_query_base_uris(
                    "grumpy",
                    {"tags": ["good"]}
                )
                result = mongo_search.search(query)
                assert len(result) == 1

                # Tag test 2.
                query = preprocess_query_base_uris(
                    "grumpy",
                    {"tags": ["good", "evil"]}
                )
                result = mongo_search.search(query)
                assert len(result) == 0

                # Tag test 3.
                query = preprocess_query_base_uris(
                    "grumpy",
                    {"tags": ["fruit", "evil"]}
                )
                result = mongo_search.search(query)
                assert len(result) == 2

                # Combination query test 1.
                query = preprocess_query_base_uris(
                    "grumpy",
                    {"free_text": "crazystuff", "tags": ["good"]}
                )
                result = mongo_search.search(query)
                assert len(result) == 1

                # Combination query test 2.
                query = preprocess_query_base_uris(
                    "grumpy",
                    {"free_text": "crazystuff", "tags": ["evil"]}
                )
                result = mongo_search.search(query)
                assert len(result) == 0


# Test the _dict_to_mongo_query helper function.
from dtool_lookup_server.utils_search import _dict_to_mongo_query

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