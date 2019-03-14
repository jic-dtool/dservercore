"""Test utils.list_datasets_by_user() helper function."""

from . import tmp_app  # NOQA


def test_list_datasets_by_user(tmp_app):  # NOQA

    from dtool_lookup_server.utils import (
        register_users,
        register_base_uri,
        update_all_permissions_on_base_uri,
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
        "name": "ds_1"
    }
    admin_metadata_2 = {
        "base_uri": base_uri_2,
        "uuid": uuid_2,
        "uri": uri_2,
        "name": "ds_2"
    }
    register_dataset_admin_metadata(admin_metadata_1)
    register_dataset_admin_metadata(admin_metadata_2)

    permissions_1 = {
        "base_uri": base_uri_1,
        "search_users": [username_1],
        "register_users": []
    }
    permissions_2 = {
        "base_uri": base_uri_2,
        "search_users": [username_1, username_2],
        "register_users": []
    }
    update_all_permissions_on_base_uri(permissions_1)
    update_all_permissions_on_base_uri(permissions_2)

    expected_content = [admin_metadata_1, admin_metadata_2]
    assert list_datasets_by_user(username_1) == expected_content

    expected_content = [admin_metadata_2]
    assert list_datasets_by_user(username_2) == expected_content
