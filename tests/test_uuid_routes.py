"""Test the /uuids blueprint routes."""

import json

def test_uuid_lookup_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data_client.get(
        "/uuids/{}".format(uuid),
        headers=headers
    )
    assert r.status_code == 200

    assert len(json.loads(r.data.decode("utf-8"))) == 2

    r = tmp_app_with_data_client.get(
        "/uuids/{}".format(uuid),
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode("utf-8")) == []

    r = tmp_app_with_data_client.get(
        "/uuids/{}".format(uuid),
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401