"""Audit regression test: searching by UUID through the API must match
datasets stored in the search index.

The marshmallow UUID field used to deserialize query UUIDs into
uuid.UUID objects, which pymongo encodes as BSON Binary - these never
matched the uuid *strings* stored in the search index, so a uuids
filter silently returned no results.
"""

import json


def test_search_uris_by_uuid(tmp_app_with_data_client, grumpy_token):  # NOQA
    """tmp_app_with_data registers datasets with this UUID for grumpy."""
    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    response = tmp_app_with_data_client.post(
        "/uris",
        data=json.dumps({"uuids": [uuid]}),
        headers={
            "Authorization": "Bearer {}".format(grumpy_token),
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 200
    hits = response.get_json()
    assert len(hits) > 0
    assert all(hit["uuid"] == uuid for hit in hits)


def test_search_uris_by_uuid_uppercase_normalized(
        tmp_app_with_data_client, grumpy_token):  # NOQA
    """UUIDs are case-insensitive; queries must normalize."""
    uuid = "AF6727BF-29C7-43DD-B42F-A5D7EDE28337"
    response = tmp_app_with_data_client.post(
        "/uris",
        data=json.dumps({"uuids": [uuid]}),
        headers={
            "Authorization": "Bearer {}".format(grumpy_token),
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 200
    assert len(response.get_json()) > 0


def test_search_uris_by_invalid_uuid_rejected(
        tmp_app_with_data_client, grumpy_token):  # NOQA
    response = tmp_app_with_data_client.post(
        "/uris",
        data=json.dumps({"uuids": ["not-a-uuid"]}),
        headers={
            "Authorization": "Bearer {}".format(grumpy_token),
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 422
