"""Test the /uris blueprint routes."""

import json

from dservercore.utils import uri_to_url_suffix


def test_list_uri_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    bad_apples_on_mr_men = {
        'base_uri': 's3://mr-men',
        'created_at': 1536238185.881941,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881941,
        'name': 'bad-apples',
        'number_of_items': 1,
        'size_in_bytes': 5741810,
        'uri': 's3://mr-men/af6727bf-29c7-43dd-b42f-a5d7ede28337',
        'uuid': 'af6727bf-29c7-43dd-b42f-a5d7ede28337'
    }
    oranges_on_snow_white = {
        'base_uri': 's3://snow-white',
        'created_at': 1536238185.881941,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881941,
        'name': 'oranges',
        'number_of_items': 0,
        'size_in_bytes': 0,
        'uri': 's3://snow-white/a2218059-5bd0-4690-b090-062faf08e046',
        'uuid': 'a2218059-5bd0-4690-b090-062faf08e046'
    }
    bad_apples_on_snow_white = {
        'base_uri': 's3://snow-white',
        'created_at': 1536238185.881941,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881941,
        'name': 'bad-apples',
        'number_of_items': 1,
        'size_in_bytes': 5741810,
        'uri': 's3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337',
        'uuid': 'af6727bf-29c7-43dd-b42f-a5d7ede28337'
    }

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

    expected_order = [
        bad_apples_on_mr_men, oranges_on_snow_white, bad_apples_on_snow_white
    ]
    assert hits == expected_order

    # sorting by name and base uri
    r = tmp_app_with_data_client.get(
        "/uris",
        query_string={'sort': '+name,-base_uri'},
        headers=headers
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        bad_apples_on_snow_white, bad_apples_on_mr_men, oranges_on_snow_white,
    ]
    assert hits == expected_order

    # sorting by uuid and uri
    r = tmp_app_with_data_client.get(
        "/uris",
        query_string={'sort': '+uuid,-uri'},
        headers=headers
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        oranges_on_snow_white, bad_apples_on_snow_white, bad_apples_on_mr_men
    ]
    assert hits == expected_order

    # sorting by uuid and uri with pagination
    r = tmp_app_with_data_client.get(
        "/uris",
        query_string={'sort': '-uuid,+uri', 'page': 1, 'page_size': 2},
        headers=headers
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        bad_apples_on_mr_men, bad_apples_on_snow_white
    ]
    assert hits == expected_order

    r = tmp_app_with_data_client.get(
        "/uris",
        query_string={'sort': '-uuid,+uri', 'page': 2, 'page_size': 2},
        headers=headers
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        oranges_on_snow_white
    ]
    assert hits == expected_order

    # check response for others
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


def test_get_dataset_by_uri_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    uri = "s3://mr-men/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    bad_apples_on_mr_men = {
        'base_uri': 's3://mr-men',
        'created_at': 1536238185.881941,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881941,
        'name': 'bad-apples',
        'number_of_items': 1,
        'size_in_bytes': 5741810,
        'uri': 's3://mr-men/af6727bf-29c7-43dd-b42f-a5d7ede28337',
        'uuid': 'af6727bf-29c7-43dd-b42f-a5d7ede28337'
    }

    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data_client.get(
        "/uris/{}".format(url_suffix),
        headers=headers
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode("utf-8")) == bad_apples_on_mr_men

    # user has no search permission on base uri
    r = tmp_app_with_data_client.get(
        "/uris/{}".format(url_suffix),
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    # user does not have search rights on the base uri;
    assert r.status_code == 403  # forbidden

    # user does not exist
    r = tmp_app_with_data_client.get(
        "/uris/{}".format(url_suffix),
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401  # unauthorized

    # dataset entry does not exist
    uri = "s3://mr-men/non-existent-dataset"
    url_suffix = uri_to_url_suffix(uri)
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data_client.get(
        "/uris/{}".format(url_suffix),
        headers=headers
    )

    # user has search access to base uri, but entry does not exist
    assert r.status_code == 404  # not found


def test_put_dataset_by_uri_route(
        tmp_app_with_users_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    from dservercore.utils import (
        get_admin_metadata_from_uri,
        lookup_datasets_by_user_and_uuid,
    )

    base_uri = "s3://snow-white"
    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "type": "dataset",
        "readme": "---\ndescription: test dataset",
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {
                "e4cc3a7dc281c3d89ed4553293c4b4b110dc9bf3": {
                    "hash": "d89117c9da2cc34586e183017cb14851",
                    "relpath": "U00096.3.rev.1.bt2",
                    "size_in_bytes": 5741810,
                    "utc_timestamp": 1536832115.0
                }
            }
        },
        "creator_username": "olssont",
        "frozen_at": "1536238185.881941",
        "annotations": {"software": "bowtie2"},
        "tags": ["rnaseq"],
        "number_of_items": 1,
        "size_in_bytes": 5741810,
    }

    url_suffix = uri_to_url_suffix(uri)

    # test for unregistered users
    headers = dict(Authorization="Bearer " + dopey_token)
    r = tmp_app_with_users_client.put(
        f"/uris/{url_suffix}",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 401

    # test for users without register permission
    headers = dict(Authorization="Bearer " + sleepy_token)
    r = tmp_app_with_users_client.put(
        f"/uris/{url_suffix}",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 403

    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.put(
        f"/uris/{url_suffix}",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 201

    # do not check against README as updating README mus happen and be tested
    # in retrieve plugin, and the implementation of a register_dataset method
    # is not enforced on a plugin
    # assert get_readme_from_uri_by_user("sleepy", uri) == dataset_info["readme"]

    expected_content = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536238185.881941,
        "number_of_items": 1,
        "size_in_bytes": 5741810,
    }
    assert get_admin_metadata_from_uri(uri) == expected_content

    assert len(lookup_datasets_by_user_and_uuid("grumpy", uuid)) == 1

    # Add the same dataset again, but with updated readme info.
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "type": "dataset",
        "readme": "---\ndescription: new metadata",
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {
                "e4cc3a7dc281c3d89ed4553293c4b4b110dc9bf3": {
                    "hash": "d89117c9da2cc34586e183017cb14851",
                    "relpath": "U00096.3.rev.1.bt2",
                    "size_in_bytes": 5741810,
                    "utc_timestamp": 1536832115.0
                }
            }
        },
        "creator_username": "olssont",
        "frozen_at": "1536238185.881941",
        "annotations": {"software": "bowtie2"},
        "tags": ["rnaseq"],
        "number_of_items": 1,
        "size_in_bytes": 15741810,
    }
    r = tmp_app_with_users_client.put(
        f"/uris/{url_suffix}",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 200  # updated, not created

    expected_content = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536238185.881941,
        "number_of_items": 1,
        "size_in_bytes": 15741810,
    }

    # do not check against README as updating README mus happen and be tested
    # in retrieve plugin, and the implementation of a register_dataset method
    # is not enforced on a plugin
    # assert get_readme_from_uri_by_user("sleepy", uri) == dataset_info["readme"]
    assert get_admin_metadata_from_uri(uri) == expected_content
    assert len(lookup_datasets_by_user_and_uuid("grumpy", uuid)) == 1

    # URI suffix and dataset uri attribute disagree
    r = tmp_app_with_users_client.put(
        f"/uris/{url_suffix}-diverges",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 400

    # Try to put invalid data.
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
    }
    r = tmp_app_with_users_client.put(
        f"/uris/{url_suffix}",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 400

    # Try to put data from user that does not exist in the system.
    headers = dict(Authorization="Bearer " + noone_token)
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "type": "dataset",
        "readme": "---\ndescription: new metadata",
        "creator_username": "olssont",
        "frozen_at": "1536238185.881941",
    }
    r = tmp_app_with_users_client.put(
        f"/uris/{url_suffix}",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 401


def test_put_dataset_route_when_created_at_is_string(
        tmp_app_with_users_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    from dservercore.utils import (
        get_admin_metadata_from_uri,
        lookup_datasets_by_user_and_uuid,
    )

    base_uri = "s3://snow-white"
    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "type": "dataset",
        "readme": "---\ndescription: test dataset",
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {
                "e4cc3a7dc281c3d89ed4553293c4b4b110dc9bf3": {
                    "hash": "d89117c9da2cc34586e183017cb14851",
                    "relpath": "U00096.3.rev.1.bt2",
                    "size_in_bytes": 5741810,
                    "utc_timestamp": 1536832115.0
                }
            }
        },
        "creator_username": "olssont",
        "frozen_at": "1536238185.881941",
        "created_at": "1536238185.881941",
        "number_of_items": 1,
        "size_in_bytes": 5741810,
        "annotations": {"software": "bowtie2"},
        "tags": ["rnaseq"],
    }

    url_suffix = uri_to_url_suffix(uri)

    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users_client.put(
        f"/uris/{url_suffix}",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 201

    expected_content = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536238185.881941,
        "number_of_items": 1,
        "size_in_bytes": 5741810,
    }
    assert get_admin_metadata_from_uri(uri) == expected_content

    assert len(lookup_datasets_by_user_and_uuid("grumpy", uuid)) == 1


def test_delete_dataset_by_uri_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    uri = "s3://mr-men/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    # dataset exists
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data_client.get(
        "/uris/{}".format(url_suffix),
        headers=headers
    )
    assert r.status_code == 200

    # try to delete, but user has no register permission on base uri
    r = tmp_app_with_data_client.delete(
        "/uris/{}".format(url_suffix),
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    # user does not have register rights on delete from base uri;
    assert r.status_code == 403  # forbidden

    # user does not exist
    r = tmp_app_with_data_client.delete(
        "/uris/{}".format(url_suffix),
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401  # unauthorized

    # delete existing dataset
    r = tmp_app_with_data_client.delete(
        "/uris/{}".format(url_suffix),
        headers=dict(Authorization="Bearer " + grumpy_token)
    )
    assert r.status_code == 200  # success

    # make sure dataset disappeared
    r = tmp_app_with_data_client.get(
        "/uris/{}".format(url_suffix),
        headers=headers
    )
    assert r.status_code == 404 # not found

    # delete again, idempotency
    r = tmp_app_with_data_client.delete(
        "/uris/{}".format(url_suffix),
        headers=dict(Authorization="Bearer " + grumpy_token)
    )
    assert r.status_code == 200  # success

    # delete dataset entry that did not exist in the first place
    uri = "s3://mr-men/non-existent-dataset"
    url_suffix = uri_to_url_suffix(uri)
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data_client.delete(
        "/uris/{}".format(url_suffix),
        headers=headers
    )

    # user has search access to base uri, but entry does not exist
    assert r.status_code == 200  # success anyway, dataset did not and does not exist


def test_uris_get_route_with_query(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    # response from internal sql db
    bad_apples_on_mr_men = {
        'base_uri': 's3://mr-men',
        'created_at': 1536238185.881941,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881941,
        'name': 'bad-apples',
        "number_of_items": 1,
        "size_in_bytes": 5741810,
        'uri': 's3://mr-men/af6727bf-29c7-43dd-b42f-a5d7ede28337',
        'uuid': 'af6727bf-29c7-43dd-b42f-a5d7ede28337'
    }
    oranges_on_snow_white = {
        'base_uri': 's3://snow-white',
        'created_at': 1536238185.881941,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881941,
        'name': 'oranges',
        "number_of_items": 0,
        "size_in_bytes": 0,
        'uri': 's3://snow-white/a2218059-5bd0-4690-b090-062faf08e046',
        'uuid': 'a2218059-5bd0-4690-b090-062faf08e046'
    }
    bad_apples_on_snow_white = {
        'base_uri': 's3://snow-white',
        'created_at': 1536238185.881941,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881941,
        'name': 'bad-apples',
        "number_of_items": 1,
        "size_in_bytes": 5741810,
        'uri': 's3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337',
        'uuid': 'af6727bf-29c7-43dd-b42f-a5d7ede28337'
    }

    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {}  # Everything.
    r = tmp_app_with_data_client.get(
        "/uris",
        headers=headers,
        query_string=query,
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    assert len(hits) == 3
    expected_order = [
        bad_apples_on_mr_men, oranges_on_snow_white, bad_apples_on_snow_white
    ]
    assert hits == expected_order

    # Make sure that timestamps are returned as float.
    first_entry = hits[0]
    assert isinstance(first_entry["created_at"], float)
    assert isinstance(first_entry["frozen_at"], float)

    r = tmp_app_with_data_client.get(
        "/uris",
        headers=dict(Authorization="Bearer " + sleepy_token),
        query_string=query,
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 0

    r = tmp_app_with_data_client.get(
        "/uris",
        headers=dict(Authorization="Bearer " + dopey_token),
        query_string=query,
    )
    assert r.status_code == 401

    r = tmp_app_with_data_client.get(
        "/uris",
        headers=dict(Authorization="Bearer " + noone_token),
        query_string=query,
    )
    assert r.status_code == 401

    # response from MongoDB in mongo search plugin
    bad_apples_on_mr_men = {
        'base_uri': 's3://mr-men',
        'created_at': 1536238185.881,  # ATTENTION: the timestamp is truncated when coming out of the mongo search plugin
        'creator_username': 'queen',
        'frozen_at': 1536238185.881,
        'name': 'bad-apples',
        'number_of_items': 1,
        'size_in_bytes': 5741810,
        'uri': 's3://mr-men/af6727bf-29c7-43dd-b42f-a5d7ede28337',
        'uuid': 'af6727bf-29c7-43dd-b42f-a5d7ede28337'
    }
    oranges_on_snow_white = {
        'base_uri': 's3://snow-white',
        'created_at': 1536238185.881,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881,
        'name': 'oranges',
        'number_of_items': 0,
        'size_in_bytes': 0,
        'uri': 's3://snow-white/a2218059-5bd0-4690-b090-062faf08e046',
        'uuid': 'a2218059-5bd0-4690-b090-062faf08e046'
    }
    bad_apples_on_snow_white = {
        'base_uri': 's3://snow-white',
        'created_at': 1536238185.881,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881,
        'name': 'bad-apples',
        'number_of_items': 1,
        'size_in_bytes': 5741810,
        'uri': 's3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337',
        'uuid': 'af6727bf-29c7-43dd-b42f-a5d7ede28337'
    }

    # search by creator_username
    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"creator_usernames": ["queen"]}  # still everything, all the same creator
    r = tmp_app_with_data_client.get(
        "/uris",
        headers=headers,
        query_string=query,
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    assert len(hits) == 3
    expected_order = [
        bad_apples_on_mr_men, oranges_on_snow_white, bad_apples_on_snow_white
    ]
    assert hits == expected_order

    # sorting by name and base uri
    r = tmp_app_with_data_client.get(
        "/uris",
        query_string={**query, 'sort': '+name,-base_uri'},
        headers=headers
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        bad_apples_on_snow_white, bad_apples_on_mr_men, oranges_on_snow_white,
    ]
    assert hits == expected_order

    # sorting by uuid and uri
    r = tmp_app_with_data_client.get(
        "/uris",
        query_string={**query, 'sort': '+uuid,-uri'},
        headers=headers
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        oranges_on_snow_white, bad_apples_on_snow_white, bad_apples_on_mr_men
    ]
    assert hits == expected_order

    # sorting by uuid and uri with pagination
    r = tmp_app_with_data_client.get(
        "/uris",
        query_string={**query, 'sort': '-uuid,+uri', 'page': 1, 'page_size': 2},
        headers=headers
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        bad_apples_on_mr_men, bad_apples_on_snow_white
    ]
    assert hits == expected_order

    r = tmp_app_with_data_client.get(
        "/uris",
        query_string={**query, 'sort': '-uuid,+uri', 'page': 2, 'page_size': 2},
        headers=headers
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        oranges_on_snow_white
    ]
    assert hits == expected_order

    # Search for apples (in README).
    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"free_text": "apple"}
    r = tmp_app_with_data_client.get(
        "/uris",
        headers=headers,
        query_string=query
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    assert len(hits) == 2
    expected_order = [
        bad_apples_on_mr_men, bad_apples_on_snow_white
    ]
    assert hits == expected_order

    # Search for U00096 (in manifest).
    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"free_text": "U00096"}
    r = tmp_app_with_data_client.get(
        "/uris",
        headers=headers,
        query_string=query
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    assert len(hits) == 2
    expected_order = [
        bad_apples_on_mr_men, bad_apples_on_snow_white
    ]
    assert hits == expected_order

    # Search for crazystuff (in annotaitons).
    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"free_text": "crazystuff"}
    r = tmp_app_with_data_client.get(
        "/uris",
        headers=headers,
        query_string=query
    )
    assert r.status_code == 200
    hits = json.loads(r.data.decode("utf-8"))
    assert len(hits) == 1
    expected_order = [
        oranges_on_snow_white
    ]
    assert hits == expected_order


def test_uris_post_route_with_query(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {}  # Everything.
    r = tmp_app_with_data_client.post(
        "/uris",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    assert len(json.loads(r.data.decode("utf-8"))) == 3

    # Make sure that timestamps are returned as float.
    first_entry = hits[0]
    assert isinstance(first_entry["created_at"], float)
    assert isinstance(first_entry["frozen_at"], float)

    r = tmp_app_with_data_client.post(
        "/uris",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 0

    r = tmp_app_with_data_client.post(
        "/uris",
        headers=dict(Authorization="Bearer " + dopey_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    r = tmp_app_with_data_client.post(
        "/uris",
        headers=dict(Authorization="Bearer " + noone_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    # response from MongoDB in mongo search plugin
    bad_apples_on_mr_men = {
        'base_uri': 's3://mr-men',
        'created_at': 1536238185.881,
        # ATTENTION: the timestamp is truncated when coming out of the mongo search plugin
        'creator_username': 'queen',
        'frozen_at': 1536238185.881,
        'name': 'bad-apples',
        'number_of_items': 1,
        'size_in_bytes': 5741810,
        'uri': 's3://mr-men/af6727bf-29c7-43dd-b42f-a5d7ede28337',
        'uuid': 'af6727bf-29c7-43dd-b42f-a5d7ede28337'
    }
    oranges_on_snow_white = {
        'base_uri': 's3://snow-white',
        'created_at': 1536238185.881,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881,
        'name': 'oranges',
        'number_of_items': 0,
        'size_in_bytes': 0,
        'uri': 's3://snow-white/a2218059-5bd0-4690-b090-062faf08e046',
        'uuid': 'a2218059-5bd0-4690-b090-062faf08e046'
    }
    bad_apples_on_snow_white = {
        'base_uri': 's3://snow-white',
        'created_at': 1536238185.881,
        'creator_username': 'queen',
        'frozen_at': 1536238185.881,
        'name': 'bad-apples',
        'number_of_items': 1,
        'size_in_bytes': 5741810,
        'uri': 's3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337',
        'uuid': 'af6727bf-29c7-43dd-b42f-a5d7ede28337'
    }

    # search by creator_username
    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"creator_usernames": ["queen"]}  # still everything, all the same creator
    r = tmp_app_with_data_client.post(
        "/uris",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    assert len(hits) == 3
    expected_order = [
        bad_apples_on_mr_men, oranges_on_snow_white, bad_apples_on_snow_white
    ]
    assert hits == expected_order

    # sorting by name and base uri
    r = tmp_app_with_data_client.post(
        "/uris",
        query_string={'sort': '+name,-base_uri'},
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        bad_apples_on_snow_white, bad_apples_on_mr_men, oranges_on_snow_white,
    ]
    assert hits == expected_order

    # sorting by uuid and uri
    r = tmp_app_with_data_client.post(
        "/uris",
        query_string={'sort': '+uuid,-uri'},
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        oranges_on_snow_white, bad_apples_on_snow_white, bad_apples_on_mr_men
    ]
    assert hits == expected_order

    # sorting by uuid and uri with pagination
    r = tmp_app_with_data_client.post(
        "/uris",
        query_string={'sort': '-uuid,+uri', 'page': 1, 'page_size': 2},
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        bad_apples_on_mr_men, bad_apples_on_snow_white
    ]
    assert hits == expected_order

    r = tmp_app_with_data_client.post(
        "/uris",
        query_string={'sort': '-uuid,+uri', 'page': 2, 'page_size': 2},
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    expected_order = [
        oranges_on_snow_white
    ]
    assert hits == expected_order

    # Search for apples (in README).
    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"free_text": "apple"}
    r = tmp_app_with_data_client.post(
        "/uris",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    assert len(json.loads(r.data.decode("utf-8"))) == 2

    # Search for U00096 (in manifest).
    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"free_text": "U00096"}
    r = tmp_app_with_data_client.post(
        "/uris",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    assert len(json.loads(r.data.decode("utf-8"))) == 2

    # Search for crazystuff (in annotaitons).
    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"free_text": "crazystuff"}
    r = tmp_app_with_data_client.post(
        "/uris",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    assert len(json.loads(r.data.decode("utf-8"))) == 1


def test_filter_based_on_tags(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)

    query = {"tags": ["good"]}
    r = tmp_app_with_data_client.get(
        "/uris",
        headers=headers,
        query_string=query
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 1

    r = tmp_app_with_data_client.post(
        "/uris",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 1

    query = {"tags": ["good", "evil"]}
    r = tmp_app_with_data_client.get(
        "/uris",
        headers=headers,
        query_string=query
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 0

    r = tmp_app_with_data_client.post(
        "/uris",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 0

    query = {"tags": ["fruit", "evil"]}
    r = tmp_app_with_data_client.get(
        "/uris",
        headers=headers,
        query_string=query
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 2

    r = tmp_app_with_data_client.post(
        "/uris",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 2


def test_combination_query(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)

    query = {"free_text": "crazystuff", "tags": ["good"]}
    r = tmp_app_with_data_client.get(
        "/uris",
        headers=headers,
        query_string=query
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 1

    r = tmp_app_with_data_client.post(
        "/uris",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 1

    query = {"free_text": "crazystuff", "tags": ["evil"]}
    r = tmp_app_with_data_client.get(
        "/uris",
        headers=headers,
        query_string=query
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 0

    r = tmp_app_with_data_client.post(
        "/uris",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 0