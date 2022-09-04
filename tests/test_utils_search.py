"""Test the search utility functions."""

# TODO: copy over all the tests from test_dict_to_mongo_query.py
# TODO: rework and add all search tests from test_dataset_routes.py
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

                query = preprocess_query_base_uris("grumpy", {})
                result = mongo_search.search(query)
                assert len(result) == 3


