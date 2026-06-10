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
            'username': 'grumpy',
            'display_name': None
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
            'username': 'grumpy',
            'display_name': None
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
            'username': 'grumpy',
            'display_name': None
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
            'username': 'dopey',
            'display_name': None
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
            'username': 'snow-white',
            'display_name': None
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
            'username': 'grumpy',
            'display_name': None
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
        {'display_name': None, 'is_admin': False, 'username': 'grumpy',
         'register_permissions_on_base_uris': ['s3://snow-white'],
         'search_permissions_on_base_uris': ['s3://snow-white']},
        {'display_name': None, 'is_admin': False, 'username': 'sleepy',
         'register_permissions_on_base_uris': [],
         'search_permissions_on_base_uris': ['s3://snow-white']},
        {'display_name': None, 'is_admin': True, 'username': 'snow-white',
         'register_permissions_on_base_uris': [],
         'search_permissions_on_base_uris': []}
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
        {'display_name': None, 'is_admin': True, 'username': 'snow-white',
         'register_permissions_on_base_uris': [],
         'search_permissions_on_base_uris': []},
        {'display_name': None, 'is_admin': False, 'username': 'sleepy',
         'register_permissions_on_base_uris': [],
         'search_permissions_on_base_uris': ['s3://snow-white']},
        {'display_name': None, 'is_admin': False, 'username': 'grumpy',
         'register_permissions_on_base_uris': ['s3://snow-white'],
         'search_permissions_on_base_uris': ['s3://snow-white']}
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


def test_grant_search_permission_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):
    """Test granting search permission via POST."""

    from dservercore.sql_models import UserWithPermissionsSchema

    # 1 - Admin grants search permission to sleepy on s3://snow-white
    # sleepy already has search permission, so we need to first check
    # the initial state then test with a new base_uri
    headers = dict(Authorization="Bearer " + snowwhite_token)

    # First, register a new base URI for testing
    from dservercore.utils import register_base_uri
    register_base_uri("s3://test-bucket")

    # Grant search permission - should succeed with 200
    r = tmp_app_with_users_client.post(
        "/users/sleepy/search/s3://test-bucket",
        headers=headers,
        json={}
    )
    assert r.status_code == 200

    user_response = r.json
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0
    assert "s3://test-bucket" in user_response["search_permissions_on_base_uris"]

    # 2 - Try to grant the same permission again - should return 409 Conflict
    r = tmp_app_with_users_client.post(
        "/users/sleepy/search/s3://test-bucket",
        headers=headers,
        json={}
    )
    assert r.status_code == 409

    # 3 - Non-admin (grumpy) tries to grant permission - should return 403
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.post(
        "/users/sleepy/search/s3://test-bucket",
        headers=headers,
        json={}
    )
    assert r.status_code == 403

    # 4 - Unregistered user (noone) tries to grant permission - should return 401
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.post(
        "/users/sleepy/search/s3://test-bucket",
        headers=headers,
        json={}
    )
    assert r.status_code == 401

    # 5 - Admin tries to grant permission to non-existent user - should return 404
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.post(
        "/users/nonexistent/search/s3://test-bucket",
        headers=headers,
        json={}
    )
    assert r.status_code == 404

    # 6 - Admin tries to grant permission on non-existent base URI - should return 404
    r = tmp_app_with_users_client.post(
        "/users/sleepy/search/s3://nonexistent-bucket",
        headers=headers,
        json={}
    )
    assert r.status_code == 404


def test_revoke_search_permission_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):
    """Test revoking search permission via DELETE."""

    from dservercore.sql_models import UserWithPermissionsSchema

    # Initial state: grumpy and sleepy have search permissions on s3://snow-white
    headers = dict(Authorization="Bearer " + snowwhite_token)

    # 1 - Admin revokes search permission from sleepy
    r = tmp_app_with_users_client.delete(
        "/users/sleepy/search/s3://snow-white",
        headers=headers
    )
    assert r.status_code == 200

    user_response = r.json
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0
    assert "s3://snow-white" not in user_response["search_permissions_on_base_uris"]

    # 2 - Revoking permission that doesn't exist should still succeed (idempotent)
    r = tmp_app_with_users_client.delete(
        "/users/sleepy/search/s3://snow-white",
        headers=headers
    )
    assert r.status_code == 200

    # 3 - Non-admin (grumpy) tries to revoke permission - should return 403
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.delete(
        "/users/sleepy/search/s3://snow-white",
        headers=headers
    )
    assert r.status_code == 403

    # 4 - Unregistered user (noone) tries to revoke permission - should return 401
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.delete(
        "/users/sleepy/search/s3://snow-white",
        headers=headers
    )
    assert r.status_code == 401

    # 5 - Admin tries to revoke permission from non-existent user - should return 404
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.delete(
        "/users/nonexistent/search/s3://snow-white",
        headers=headers
    )
    assert r.status_code == 404

    # 6 - Admin tries to revoke permission on non-existent base URI - should return 404
    r = tmp_app_with_users_client.delete(
        "/users/sleepy/search/s3://nonexistent-bucket",
        headers=headers
    )
    assert r.status_code == 404


def test_grant_register_permission_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):
    """Test granting register permission via POST."""

    from dservercore.sql_models import UserWithPermissionsSchema

    headers = dict(Authorization="Bearer " + snowwhite_token)

    # 1 - Admin grants register permission to sleepy on s3://snow-white
    # sleepy does not have register permission initially
    r = tmp_app_with_users_client.post(
        "/users/sleepy/register/s3://snow-white",
        headers=headers,
        json={}
    )
    assert r.status_code == 200

    user_response = r.json
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0
    assert "s3://snow-white" in user_response["register_permissions_on_base_uris"]

    # 2 - Try to grant the same permission again - should return 409 Conflict
    r = tmp_app_with_users_client.post(
        "/users/sleepy/register/s3://snow-white",
        headers=headers,
        json={}
    )
    assert r.status_code == 409

    # 3 - Non-admin (grumpy) tries to grant permission - should return 403
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.post(
        "/users/sleepy/register/s3://snow-white",
        headers=headers,
        json={}
    )
    assert r.status_code == 403

    # 4 - Unregistered user (noone) tries to grant permission - should return 401
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.post(
        "/users/sleepy/register/s3://snow-white",
        headers=headers,
        json={}
    )
    assert r.status_code == 401

    # 5 - Admin tries to grant permission to non-existent user - should return 404
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.post(
        "/users/nonexistent/register/s3://snow-white",
        headers=headers,
        json={}
    )
    assert r.status_code == 404

    # 6 - Admin tries to grant permission on non-existent base URI - should return 404
    r = tmp_app_with_users_client.post(
        "/users/sleepy/register/s3://nonexistent-bucket",
        headers=headers,
        json={}
    )
    assert r.status_code == 404


def test_revoke_register_permission_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):
    """Test revoking register permission via DELETE."""

    from dservercore.sql_models import UserWithPermissionsSchema

    # Initial state: grumpy has register permission on s3://snow-white
    headers = dict(Authorization="Bearer " + snowwhite_token)

    # 1 - Admin revokes register permission from grumpy
    r = tmp_app_with_users_client.delete(
        "/users/grumpy/register/s3://snow-white",
        headers=headers
    )
    assert r.status_code == 200

    user_response = r.json
    assert len(UserWithPermissionsSchema().validate(user_response)) == 0
    assert "s3://snow-white" not in user_response["register_permissions_on_base_uris"]

    # 2 - Revoking permission that doesn't exist should still succeed (idempotent)
    r = tmp_app_with_users_client.delete(
        "/users/grumpy/register/s3://snow-white",
        headers=headers
    )
    assert r.status_code == 200

    # 3 - Non-admin (sleepy) tries to revoke permission - should return 403
    headers = dict(Authorization="Bearer " + sleepy_token)
    r = tmp_app_with_users_client.delete(
        "/users/grumpy/register/s3://snow-white",
        headers=headers
    )
    assert r.status_code == 403

    # 4 - Unregistered user (noone) tries to revoke permission - should return 401
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.delete(
        "/users/grumpy/register/s3://snow-white",
        headers=headers
    )
    assert r.status_code == 401

    # 5 - Admin tries to revoke permission from non-existent user - should return 404
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users_client.delete(
        "/users/nonexistent/register/s3://snow-white",
        headers=headers
    )
    assert r.status_code == 404

    # 6 - Admin tries to revoke permission on non-existent base URI - should return 404
    r = tmp_app_with_users_client.delete(
        "/users/grumpy/register/s3://nonexistent-bucket",
        headers=headers
    )
    assert r.status_code == 404
