"""Test the _dict_to_mongo_query helper function."""


def test_empty_dict():
    """An empty dict should return query for all datasets."""
    from dtool_lookup_server.utils import _dict_to_mongo_query
    assert _dict_to_mongo_query({}) == {}


def test_free_text():
    """Should return {"$text": {"$search": "free_text_here"}}"""
    from dtool_lookup_server.utils import _dict_to_mongo_query
    query = dict(free_text="free_text_here")
    expected_mongo_query = {"$text": {"$search": "free_text_here"}}
    assert _dict_to_mongo_query(query) == expected_mongo_query


def test_creator_usernames():
    from dtool_lookup_server.utils import _dict_to_mongo_query

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
    from dtool_lookup_server.utils import _dict_to_mongo_query

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
    from dtool_lookup_server.utils import _dict_to_mongo_query

    # Test single tag.
    query = dict(tags=["evil"])
    expected_mongo_query = {"tags": "evil"}
    assert _dict_to_mongo_query(query) == expected_mongo_query

    # Test multiple tags.
    query = dict(tags=["evil", "good"])
    expected_mongo_query = {"tags": { "$all": ["evil", "good"]}}
    assert _dict_to_mongo_query(query) == expected_mongo_query

    # Test empty list.
    query = dict(tags=[])
    assert _dict_to_mongo_query(query) == {}


def test_combinations():

    from dtool_lookup_server.utils import _dict_to_mongo_query

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
