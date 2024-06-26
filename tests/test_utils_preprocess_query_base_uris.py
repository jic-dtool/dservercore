"""Test dservercore preprocess_query_base_uris  helper function."""


def test_preprocess_query_base_uris(tmp_app_with_users_client):  # NOQA

    from dservercore.utils import preprocess_query_base_uris

    grumpy_expected_query = {"base_uris": ["s3://snow-white"]}

    # Test that all allowed are added if "base_uris" key is missing.
    grumpy_actual_query = preprocess_query_base_uris(
        username="grumpy",
        query={}
    )
    assert grumpy_actual_query == grumpy_expected_query

    # Test that base URIs that are not allowed are filtered out.
    grumpy_actual_query = preprocess_query_base_uris(
        username="grumpy",
        query={"base_uris": ["s3://snow-white", "s3://dont-exist"]}
    )
    assert grumpy_actual_query == grumpy_expected_query

    grumpy_actual_query = preprocess_query_base_uris(
        username="grumpy",
        query={"base_uris": ["s3://dont-exist"]}
    )
    assert grumpy_actual_query == {"base_uris": []}
