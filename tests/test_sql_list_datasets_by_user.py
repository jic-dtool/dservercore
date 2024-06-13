"""Test utils.list_datasets_by_user() helper function."""


def test_list_datasets_by_user(tmp_app_client):  # NOQA

    from dservercore.utils import (
        register_users,
        register_base_uri,
        register_permissions,
        register_dataset_admin_metadata,
        list_datasets_by_user,
    )

    base_uri_1 = "s3://snow-white"
    base_uri_2 = "s3://mr-men"
    register_base_uri(base_uri_1)
    register_base_uri(base_uri_2)

    username_1 = "dopey"
    username_2 = "grumpy"
    register_users([{"username": un} for un in (username_1, username_2)])

    uuid_1 = "11111111-1111-1111-1111-111111111111"
    uuid_2 = "22222222-2222-2222-2222-222222222222"
    uri_1 = "{}/{}".format(base_uri_1, uuid_1)
    uri_2 = "{}/{}".format(base_uri_2, uuid_2)

    admin_metadata_1 = {
        "base_uri": base_uri_1,
        "uuid": uuid_1,
        "uri": uri_1,
        "name": "ds_1",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536236399.19497,
        "number_of_items": 7283,
        "size_in_bytes": 5741810,
    }
    admin_metadata_2 = {
        "base_uri": base_uri_2,
        "uuid": uuid_2,
        "uri": uri_2,
        "name": "ds_2",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536236399.19497,
        "number_of_items": 392,
        "size_in_bytes": 574181,
    }
    register_dataset_admin_metadata(admin_metadata_1)
    register_dataset_admin_metadata(admin_metadata_2)

    permissions_1 = {
        # "base_uri": base_uri_1,
        "users_with_search_permissions": [username_1],
        "users_with_register_permissions": []
    }
    permissions_2 = {
        # "base_uri": base_uri_2,
        "users_with_search_permissions": [username_1, username_2],
        "users_with_register_permissions": []
    }
    register_permissions(base_uri_1, permissions_1)
    register_permissions(base_uri_2, permissions_2)

    expected_content = [admin_metadata_1, admin_metadata_2]
    retrieved_content = [ds.as_dict() for ds in list_datasets_by_user(username_1)]
    assert retrieved_content == expected_content

    expected_content = [admin_metadata_2]
    retrieved_content = [ds.as_dict() for ds in list_datasets_by_user(username_2)]
    assert retrieved_content == expected_content
