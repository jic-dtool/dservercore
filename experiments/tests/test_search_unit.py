"""Unit tests for the search module."""

import dtool_lookup_server_search as dls_search

def test_non_existing_user_is_not_admin():
    search = dls_search.Search()
    assert search.search("dont_exist") == []