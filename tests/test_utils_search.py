"""Test the search utility functions."""

# TODO: copy over all the tests from test_dict_to_mongo_query.py
# DONE: rework and add all search tests from test_dataset_routes.py
# TODO: add tests and functionality for mongo_search.register_dataset()
# TODO: add tests and functionality for mongo_search.lookup_uris()

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