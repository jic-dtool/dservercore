"""Test the /me blueprint routes."""


import json


def test_me_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):
    """Test retrieving current user information by get method."""

    from dservercore.sql_models import UserWithPermissionsSchema

    # snow-white
    headers = dict(Authorization="Bearer " + snowwhite_token)

    expected_response = UserWithPermissionsSchema().load(
        {
            'is_admin': True,
            'register_permissions_on_base_uris': [],
            'search_permissions_on_base_uris': [],
            'username': 'snow-white'
        })

    r = tmp_app_with_users_client.get(
        "/me",
        headers=headers
    )
    assert r.status_code == 200

    user_response = r.json

    # validate against expected schema
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0

    # assert correct content
    assert user_response == expected_response

    # grumpy
    expected_response = UserWithPermissionsSchema().load(
        {
            'is_admin': False,
            'register_permissions_on_base_uris': ['s3://snow-white'],
            'search_permissions_on_base_uris': ['s3://snow-white'],
            'username': 'grumpy'
        })

    headers = dict(Authorization="Bearer " + grumpy_token)

    r = tmp_app_with_users_client.get(
        "/me",
        headers=headers
    )
    assert r.status_code == 200

    user_response = r.json

    # validate against expected schema
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0

    # assert correct content
    assert user_response == expected_response

    # noone (user does not exist)
    headers = dict(Authorization="Bearer " + noone_token)

    r = tmp_app_with_users_client.get(
        "/me",
        headers=headers
    )

    assert r.status_code == 401


def test_me_summary_route(
        tmp_app_with_data_client,
        snowwhite_token,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    # snow-white
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_data_client.get(
        "/me/summary",
        headers=headers
    )
    assert r.status_code == 200

    expected_content = {
        "number_of_datasets": 0,
        "total_size_in_bytes": 0,
        "creator_usernames": [],
        "base_uris": [],
        "datasets_per_creator": {},
        "size_in_bytes_per_creator": {},
        "datasets_per_base_uri": {},
        "size_in_bytes_per_base_uri": {},
        "tags": [],
        "datasets_per_tag": {},
        "size_in_bytes_per_tag": {}
    }
    assert expected_content == json.loads(r.data.decode("utf-8"))

    # grumpy
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data_client.get(
        "/me/summary",
        headers=headers
    )
    assert r.status_code == 200

    expected_content = {
        "number_of_datasets": 3,
        "total_size_in_bytes": 11483620,
        "creator_usernames": ["queen"],
        "base_uris": ["s3://mr-men", "s3://snow-white"],
        "datasets_per_creator": {"queen": 3},
        "size_in_bytes_per_creator": {"queen": 11483620},
        "datasets_per_base_uri": {"s3://mr-men": 1, "s3://snow-white": 2},
        "size_in_bytes_per_base_uri": {"s3://mr-men": 5741810,
                                       "s3://snow-white": 5741810},
        "tags": ["evil", "fruit", "good"],
        "datasets_per_tag": {"good": 1, "evil": 2, "fruit": 3},
        "size_in_bytes_per_tag": {"evil": 11483620, "fruit": 11483620, "good": 0},
    }
    assert expected_content == json.loads(r.data.decode("utf-8"))

    # sleepy
    r = tmp_app_with_data_client.get(
        "/me/summary",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 200
    expected_content = {
        "number_of_datasets": 0,
        "total_size_in_bytes": 0,
        "creator_usernames": [],
        "base_uris": [],
        "datasets_per_creator": {},
        "size_in_bytes_per_creator": {},
        "datasets_per_base_uri": {},
        "size_in_bytes_per_base_uri": {},
        "tags": [],
        "datasets_per_tag": {},
        "size_in_bytes_per_tag": {}
    }
    assert expected_content == json.loads(r.data.decode("utf-8"))

    # dopey (not registered) checks himself
    r = tmp_app_with_data_client.get(
        "/me/summary",
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401

    # noone (not registered) checks himself
    r = tmp_app_with_data_client.get(
        "/me/summary",
        headers=dict(Authorization="Bearer " + noone_token)
    )
    assert r.status_code == 401