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

    bad_apples_on_mr_men = {
        'base_uri': 's3://mr-men',
        'created_at': 1536238185.881941,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881941,
        'name': 'bad-apples',
        'uri': 's3://mr-men/af6727bf-29c7-43dd-b42f-a5d7ede28337',
        'uuid': 'af6727bf-29c7-43dd-b42f-a5d7ede28337'
    }
    oranges_on_snow_white = {
        'base_uri': 's3://snow-white',
        'created_at': 1536238185.881941,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881941,
        'name': 'oranges',
        'uri': 's3://snow-white/a2218059-5bd0-4690-b090-062faf08e046',
        'uuid': 'a2218059-5bd0-4690-b090-062faf08e046'
    }
    bad_apples_on_snow_white = {
        'base_uri': 's3://snow-white',
        'created_at': 1536238185.881941,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881941,
        'name': 'bad-apples',
        'uri': 's3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337',
        'uuid': 'af6727bf-29c7-43dd-b42f-a5d7ede28337'
    }

    # Make sure that timestamps are returned as float.
    first_entry = hits[0]
    assert isinstance(first_entry["created_at"], float)
    assert isinstance(first_entry["frozen_at"], float)

    expected_order = [
        bad_apples_on_mr_men, oranges_on_snow_white, bad_apples_on_snow_white
    ]
    assert hits == expected_order

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