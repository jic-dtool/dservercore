"""Test the /users blueprint routes."""

import json


def test_put_user_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):  # NOQA
    """Test updating user information by put method."""

    from dservercore.sql_models import UserWithPermissionsSchema

    # 1 - check original grumpy entry
    expected_response = UserWithPermissionsSchema().load(
        {
            'is_admin': False,
            'register_permissions_on_base_uris': ['s3://snow-white'],
            'search_permissions_on_base_uris': ['s3://snow-white'],
            'username': 'grumpy'
        })

    headers = dict(Authorization="Bearer " + snowwhite_token)

    r = tmp_app_with_users_client.get(
        "/users/grumpy",
        headers=headers
    )
    assert r.status_code == 200

    user_response = r.json

    # 2 - validate against expected schema
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0

    assert user_response == expected_response

    # replace grumpy
    r = tmp_app_with_users_client.put(
        "/users/grumpy",
        headers=headers,
        json={"is_admin": True}
    )

    assert r.status_code == 200

    # check modified grumpy entry
    expected_response = UserWithPermissionsSchema().load(
        {
            'is_admin': True,
            'register_permissions_on_base_uris': ['s3://snow-white'],
            'search_permissions_on_base_uris': ['s3://snow-white'],
            'username': 'grumpy'
        })

    r = tmp_app_with_users_client.get(
        "/users/grumpy",
        headers=headers
    )
    assert r.status_code == 200

    user_response = r.json

    assert user_response == expected_response

    # 3 - check replacement of whole entry, contrary to patch
    expected_response = UserWithPermissionsSchema().load(
        {
            'is_admin': False,
            'register_permissions_on_base_uris': ['s3://snow-white'],
            'search_permissions_on_base_uris': ['s3://snow-white'],
            'username': 'grumpy'
        })

    r = tmp_app_with_users_client.put(
        "/users/grumpy",
        headers=headers,
        json={}
    )
    assert r.status_code == 200

    r = tmp_app_with_users_client.get(
        "/users/grumpy",
        headers=headers
    )
    assert r.status_code == 200

    user_response = r.json

    # validate against expected schema
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0

    assert user_response == expected_response

    # 4 - check creation for non-existing user
    r = tmp_app_with_users_client.put(
        "/users/dopey",
        headers=headers,
        json={"is_admin": True}
    )

    assert r.status_code == 201

    r = tmp_app_with_users_client.get(
        "/users/dopey",
        headers=headers
    )
    assert r.status_code == 200

    user_response = r.json
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0

    expected_response = UserWithPermissionsSchema().load(
        {
            'is_admin': True,
            'register_permissions_on_base_uris': [],
            'search_permissions_on_base_uris': [],
            'username': 'dopey'
        })

    assert user_response == expected_response

    # 5 - check failure for non-admins
    headers = dict(Authorization="Bearer " + sleepy_token)

    r = tmp_app_with_users_client.put(
        "/users/grumpy",
        headers=headers,
        json={"is_admin": True}
    )
    assert r.status_code == 403

    # 6 - check failure for non-registered users
    headers = dict(Authorization="Bearer " + noone_token)

    r = tmp_app_with_users_client.put(
        "/users/grumpy",
        headers=headers,
        json={"is_admin": True}
    )
    assert r.status_code == 401


def test_get_user_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):
    """Test retrieving user information by get method."""

    from dservercore.sql_models import UserWithPermissionsSchema

    # 1 - snow-white by snow-white
    # Admin is allowed to query any user
    headers = dict(Authorization="Bearer " + snowwhite_token)

    expected_response = UserWithPermissionsSchema().load(
        {
            'is_admin': True,
            'register_permissions_on_base_uris': [],
            'search_permissions_on_base_uris': [],
            'username': 'snow-white'
        })

    r = tmp_app_with_users_client.get(
        "/users/snow-white",
        headers=headers
    )
    assert r.status_code == 200

    user_response = r.json

    # validate against expected schema
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0

    # assert correct content
    assert user_response == expected_response

    # 2 - grumpy by snow-white
    expected_response = UserWithPermissionsSchema().load(
        {
            'is_admin': False,
            'register_permissions_on_base_uris': ['s3://snow-white'],
            'search_permissions_on_base_uris': ['s3://snow-white'],
            'username': 'grumpy'
        })

    r = tmp_app_with_users_client.get(
        "/users/grumpy",
        headers=headers
    )
    assert r.status_code == 200

    user_response = r.json

    # validate against expected schema
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0

    # assert correct content
    assert user_response == expected_response

    # 3 - noone (does not exist) by snow-white
    r = tmp_app_with_users_client.get(
        "/users/noone",
        headers=headers
    )
    assert r.status_code == 404

    # 4 - grumpy by grumpy
    # Only admins allowed to query all users.
    # Non-admins may query themselves only.
    headers = dict(Authorization="Bearer " + grumpy_token)

    r = tmp_app_with_users_client.get(
        "/users/grumpy",
        headers=headers
    )
    assert r.status_code == 200

    user_response = r.json

    # validate against expected schema
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0

    # assert correct content
    assert user_response == expected_response

    # 5 - snow-white by grumpy
    r = tmp_app_with_users_client.get(
        "/users/snow-white",
        headers=headers
    )

    assert r.status_code == 403

    # 6 - snow-white by noone (user does not exist)
    headers = dict(Authorization="Bearer " + noone_token)

    r = tmp_app_with_users_client.get(
        "/users/snow-white",
        headers=headers
    )

    assert r.status_code == 401


def test_delete_user_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):
    "Text deletein users"

    from dservercore.utils import user_exists

    assert user_exists("grumpy")

    headers = dict(Authorization="Bearer " + snowwhite_token)

    # delete grumpy
    r = tmp_app_with_users_client.delete(
        "/users/grumpy",
        headers=headers
    )
    assert r.status_code == 200
    assert not user_exists("grumpy")

    # assure idempotency
    r = tmp_app_with_users_client.delete(
        "/users/grumpy",
        headers=headers
    )
    assert r.status_code == 200
    assert not user_exists("grumpy")

    # delete non-existing user
    assert not user_exists("noone")
    r = tmp_app_with_users_client.delete(
        "/users/noone",
        headers=headers
    )
    assert r.status_code == 200
    assert not user_exists("noone")

    # check failure for non-admins
    headers = dict(Authorization="Bearer " + sleepy_token)

    r = tmp_app_with_users_client.delete(
        "/users/grumpy",
        headers=headers
    )
    assert r.status_code == 403

    # check failure for non-registered users
    headers = dict(Authorization="Bearer " + noone_token)

    r = tmp_app_with_users_client.delete(
        "/users/grumpy",
        headers=headers
    )
    assert r.status_code == 401


def test_list_user_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):  # NOQA

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.get(
        "/users",
        headers=headers,
    )
    assert r.status_code == 200

    data = r.json
    assert data == [
        {'is_admin': False, 'username': 'grumpy'},
        {'is_admin': False, 'username': 'sleepy'},
        {'is_admin': True, 'username': 'snow-white'}
    ]

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.get(
        "/users",
        headers=headers,
        query_string={"sort": "-is_admin,-username"}
    )
    assert r.status_code == 200

    data = r.json
    assert data == [
        {'is_admin': True, 'username': 'snow-white'},
        {'is_admin': False, 'username': 'sleepy'},
        {'is_admin': False, 'username': 'grumpy'}
    ]

    # Only admins allowed.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.get(
        "/users",
        headers=headers
    )
    assert r.status_code == 403

    # Non-registered users should see 401
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.get(
        "/users",
        headers=headers
    )
    assert r.status_code == 401


def test_dataset_summary_route(
        tmp_app_with_data_client,
        snowwhite_token,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    # snow-white (admin) checks herself
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_data_client.get(
        "/users/snow-white/summary",
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

    # grumpy checks himself
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data_client.get(
        "/users/grumpy/summary",
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

    # snow-white (admin) checks grumpy
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_data_client.get(
        "/users/grumpy/summary",
        headers=headers
    )
    assert r.status_code == 200
    assert expected_content == json.loads(r.data.decode("utf-8"))

    # sleepy checks himself
    r = tmp_app_with_data_client.get(
        "/users/sleepy/summary",
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

    # snow-white (admin) checks sleepy
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_data_client.get(
        "/users/sleepy/summary",
        headers=headers
    )
    assert r.status_code == 200
    assert expected_content == json.loads(r.data.decode("utf-8"))

    # grumpy (non-admin) checks sleepy
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data_client.get(
        "/users/sleepy/summary",
        headers=headers
    )
    assert r.status_code == 403

    # sleepy (non-admin) checks grumpy
    headers = dict(Authorization="Bearer " + sleepy_token)
    r = tmp_app_with_data_client.get(
        "/users/grumpy/summary",
        headers=headers
    )
    assert r.status_code == 403

    # dopey (not registered) checks himself
    r = tmp_app_with_data_client.get(
        "/users/dopey/summary",
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401

    # noone (not registered) checks himself
    r = tmp_app_with_data_client.get(
        "/users/noone/summary",
        headers=dict(Authorization="Bearer " + noone_token)
    )
    assert r.status_code == 401

    # snow-white (admin) checks noone (not registered)
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_data_client.get(
        "/users/noone/summary",
        headers=headers
    )
    assert r.status_code == 404
