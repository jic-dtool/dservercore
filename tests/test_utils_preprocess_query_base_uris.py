"""Test dtool lookup server preprocess_query_base_uris  helper function."""

from . import tmp_app_with_users  # NOQA


def test_preprocess_query_base_uris(tmp_app_with_users):  # NOQA

    from dtool_lookup_server.utils import preprocess_query_base_uris

    grumpy_expected_query = {"base_uris": ["s3://snow-white"]}
    snow_white_expected_query = {"base_uris": []}

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
