"""Test the /uris blueprint routes."""

import json


def test_list_uri_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data_client.get(
        "/uris",
        headers=headers
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    assert len(hits) == 3

    # Make sure that timestamps are returned as float.
    first_entry = hits[0]
    assert isinstance(first_entry["created_at"], float)
    assert isinstance(first_entry["frozen_at"], float)

    r = tmp_app_with_data_client.get(
        "/uris",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode("utf-8")) == []

    r = tmp_app_with_data_client.get(
        "/uris",
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401