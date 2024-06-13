"""Test that the timestamps returned from sql and mongo databases match."""


def test_timestamp_consistency(tmp_app_with_data_client):  # NOQA
    from dservercore.utils import (
        lookup_datasets_by_user_and_uuid,
        search_datasets_by_user,
    )

    username = "grumpy"
    uuid = "a2218059-5bd0-4690-b090-062faf08e046"
    expected_frozen_at = 1536238185.881941

    lookup_hits = lookup_datasets_by_user_and_uuid(username, uuid)
    assert len(lookup_hits) == 1
    lookup_hit = lookup_hits[0].as_dict()

    search_hits = search_datasets_by_user(username, {"uuids": [uuid]})
    assert len(search_hits) == 1
    search_hit = lookup_hits[0].as_dict()

    for key in ("created_at", "frozen_at"):
        assert lookup_hit[key] == search_hit[key]
        assert lookup_hit[key] == expected_frozen_at
