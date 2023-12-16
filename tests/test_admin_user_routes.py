"""Test the /admin/user blueprint routes."""

import json


def test_register_user_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):  # NOQA

    from dtool_lookup_server.utils import user_exists

    assert not user_exists("evil-witch")
    assert not user_exists("dopey")

    users = [
        {"username": "evil-witch", "is_admin": True},
        {"username": "dopey"}
    ]
    headers = dict(Authorization="Bearer " + snowwhite_token)
    for user in users:
        r = tmp_app_with_users_client.post(
            "/users/{}".format(user["username"]),
            headers=headers,
            data=json.dumps(user),
            content_type="application/json"
        )
        assert r.status_code == 201

    assert user_exists("evil-witch")
    assert user_exists("dopey")

    # Ensure idempotent.
    for user in users:
        r = tmp_app_with_users_client.post(
            "/users/{}".format(user["username"]),
            headers=headers,
            data=json.dumps(user),
            content_type="application/json"
        )
        assert r.status_code == 201

    assert user_exists("evil-witch")
    assert user_exists("dopey")

    # Only admins allowed. However, don't give away that URL exists to
    # non-admins.
    headers = dict(Authorization="Bearer " + grumpy_token)

    for user in users:
        r = tmp_app_with_users_client.post(
            "/users/{}".format(user["username"]),
            headers=headers,
            data=json.dumps(user),
            content_type="application/json"
        )
        assert r.status_code == 404

    headers = dict(Authorization="Bearer " + noone_token)
    for user in users:
        r = tmp_app_with_users_client.post(
            "/users/{}".format(user["username"]),
            headers=headers,
            data=json.dumps(user),
            content_type="application/json"
        )
        assert r.status_code == 404

def test_get_user_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):
    """Test retrieving user information by get method."""

    from dtool_lookup_server.schemas import UserResponseSchema

    # 1 - snow-white by snow-white
    # Admin is allowed to query any user
    headers = dict(Authorization="Bearer " + snowwhite_token)

    expected_response = UserResponseSchema().load(
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
    assert len(UserResponseSchema().validate(user_response)) == 0

    # assert correct content
    assert user_response == expected_response

    # 2 - grumpy by snow-white
    expected_response = UserResponseSchema().load(
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
    assert len(UserResponseSchema().validate(user_response)) == 0

    # assert correct content
    assert user_response == expected_response

    # 3 - grumpy by grumpy
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
    assert len(UserResponseSchema().validate(user_response)) == 0

    # assert correct content
    assert user_response == expected_response

    # 4 - snow-white by grumpy
    r = tmp_app_with_users_client.get(
        "/users/snow-white",
        headers=headers
    )

    print(r)
    assert r.status_code == 404


def test_patch_user_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):
    "Text updating user information by patch method."

    from dtool_lookup_server.schemas import UserResponseSchema

    # 1 - check original grumpy entry
    expected_response = UserResponseSchema().load(
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
    assert len(UserResponseSchema().validate(user_response)) == 0

    assert user_response == expected_response

    # patch grumpy
    r = tmp_app_with_users_client.patch(
        "/users/grumpy",
        headers=headers,
        json={"is_admin": True}
    )

    assert r.status_code == 200

    # check modified grumpy entry
    expected_response = UserResponseSchema().load(
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

    # 3 - check idempotency
    r = tmp_app_with_users_client.patch(
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
    assert len(UserResponseSchema().validate(user_response)) == 0

    assert user_response == expected_response

    # 4 - check failure for non-admins
    headers = dict(Authorization="Bearer " + sleepy_token)

    r = tmp_app_with_users_client.patch(
        "/users/grumpy",
        headers=headers,
        json={"is_admin": True}
    )
    assert r.status_code == 404


def test_put_user_route(
        tmp_app_with_users_client,
        snowwhite_token,
        grumpy_token,
        noone_token,
        sleepy_token):  # NOQA
    """Test updating user information by put method."""

    from dtool_lookup_server.schemas import UserResponseSchema

    # 1 - check original grumpy entry
    expected_response = UserResponseSchema().load(
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
    assert len(UserResponseSchema().validate(user_response)) == 0

    assert user_response == expected_response

    # patch grumpy
    r = tmp_app_with_users_client.put(
        "/users/grumpy",
        headers=headers,
        json={"is_admin": True}
    )

    assert r.status_code == 200

    # check modified grumpy entry
    expected_response = UserResponseSchema().load(
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
    expected_response = UserResponseSchema().load(
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
    assert len(UserResponseSchema().validate(user_response)) == 0

    assert user_response == expected_response

    # 4 - check failure for non-admins
    headers = dict(Authorization="Bearer " + sleepy_token)

    r = tmp_app_with_users_client.put(
        "/users/grumpy",
        headers=headers,
        json={"is_admin": True}
    )
    assert r.status_code == 404


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
        {'id': 1, 'is_admin': True, 'username': 'snow-white'},
        {'id': 2, 'is_admin': False, 'username': 'grumpy'},
        {'id': 3, 'is_admin': False, 'username': 'sleepy'}
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
        {'id': 1, 'is_admin': True, 'username': 'snow-white'},
        {'id': 3, 'is_admin': False, 'username': 'sleepy'},
        {'id': 2, 'is_admin': False, 'username': 'grumpy'}
    ]

    # Only admins allowed. However, don't give away that URL exists to
    # non-admins.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.get(
        "/users",
        headers=headers
    )
    assert r.status_code == 404

    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users_client.get(
        "/users",
        headers=headers
    )
    assert r.status_code == 404

