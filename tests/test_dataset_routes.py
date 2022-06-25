"""Test the /datasets blueprint routes."""

import json

from . import tmp_app, tmp_app_with_data, tmp_app_with_users  # NOQA

from . import (
    grumpy_token,
    sleepy_token,
    dopey_token,
    noone_token,
)

def test_dataset_summary_route(tmp_app_with_data):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data.get(
        "/dataset/summary",
        headers=headers
    )
    assert r.status_code == 200

    expected_content = {
        "number_of_datasets": 3,
        "creator_usernames": ["queen"],
        "base_uris": ["s3://mr-men", "s3://snow-white"],
        "datasets_per_creator": {"queen": 3},
        "datasets_per_base_uri": {"s3://mr-men": 1, "s3://snow-white": 2},
        "tags": ["evil", "fruit", "good"],
        "datasets_per_tag": {"good": 1, "evil": 2, "fruit": 3}
    }
    assert expected_content == json.loads(r.data.decode("utf-8"))

    r = tmp_app_with_data.get(
        "/dataset/summary",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 200
    expected_content = {
        "number_of_datasets": 0,
        "creator_usernames": [],
        "base_uris": [],
        "datasets_per_creator": {},
        "datasets_per_base_uri": {},
        "tags": [],
        "datasets_per_tag": {}
    }
    assert expected_content == json.loads(r.data.decode("utf-8"))

    r = tmp_app_with_data.get(
        "/dataset/summary",
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401

    r = tmp_app_with_data.get(
        "/dataset/summary",
        headers=dict(Authorization="Bearer " + noone_token)
    )
    assert r.status_code == 401


def test_dataset_list_route(tmp_app_with_data):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data.get(
        "/dataset/list",
        headers=headers
    )
    assert r.status_code == 200

    hits = json.loads(r.data.decode("utf-8"))
    assert len(hits) == 3

    # Make sure that timestamps are returned as float.
    first_entry = hits[0]
    assert isinstance(first_entry["created_at"], float)
    assert isinstance(first_entry["frozen_at"], float)

    r = tmp_app_with_data.get(
        "/dataset/list",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode("utf-8")) == []

    r = tmp_app_with_data.get(
        "/dataset/list",
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401


def test_dataset_search_route(tmp_app_with_data):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {}  # Everything.
    r = tmp_app_with_data.post(
        "/dataset/search",
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

    r = tmp_app_with_data.post(
        "/dataset/search",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 0

    r = tmp_app_with_data.post(
        "/dataset/search",
        headers=dict(Authorization="Bearer " + dopey_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    r = tmp_app_with_data.post(
        "/dataset/search",
        headers=dict(Authorization="Bearer " + noone_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    # Search for apples (in README).
    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"free_text": "apple"}
    r = tmp_app_with_data.post(
        "/dataset/search",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    assert len(json.loads(r.data.decode("utf-8"))) == 2

    # Search for U00096 (in manifest).
    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"free_text": "U00096"}
    r = tmp_app_with_data.post(
        "/dataset/search",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    assert len(json.loads(r.data.decode("utf-8"))) == 2

    # Search for crazystuff (in annotaitons).
    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"free_text": "crazystuff"}
    r = tmp_app_with_data.post(
        "/dataset/search",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    assert len(json.loads(r.data.decode("utf-8"))) == 1


def test_filter_based_on_tags(tmp_app_with_data):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)

    query = {"tags": ["good"]}
    r = tmp_app_with_data.post(
        "/dataset/search",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 1

    query = {"tags": ["good", "evil"]}
    r = tmp_app_with_data.post(
        "/dataset/search",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 0

    query = {"tags": ["fruit", "evil"]}
    r = tmp_app_with_data.post(
        "/dataset/search",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 2


def test_combination_query(tmp_app_with_data):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)

    query = {"free_text": "crazystuff", "tags": ["good"]}
    r = tmp_app_with_data.post(
        "/dataset/search",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 1

    query = {"free_text": "crazystuff", "tags": ["evil"]}
    r = tmp_app_with_data.post(
        "/dataset/search",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 0


def test_dataset_register_route(tmp_app_with_users):  # NOQA

    from dtool_lookup_server.utils import (
        get_admin_metadata_from_uri,
        get_readme_from_uri_by_user,
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

    for token in [dopey_token, sleepy_token]:
        headers = dict(Authorization="Bearer " + sleepy_token)
        r = tmp_app_with_users.post(
            "/dataset/register",
            headers=headers,
            data=json.dumps(dataset_info),
            content_type="application/json"
        )
        assert r.status_code == 401

    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users.post(
        "/dataset/register",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 201

    assert get_readme_from_uri_by_user("sleepy", uri) == dataset_info["readme"]

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
        "size_in_bytes": 1536238185.881941,
    }
    r = tmp_app_with_users.post(
        "/dataset/register",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 201

    assert get_readme_from_uri_by_user("sleepy", uri) == dataset_info["readme"]
    assert get_admin_metadata_from_uri(uri) == expected_content
    assert len(lookup_datasets_by_user_and_uuid("grumpy", uuid)) == 1

    # Try to post invalid data.
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
    }
    r = tmp_app_with_users.post(
        "/dataset/register",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 409

    # Try to post data from user that does not exist in the system.
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
    r = tmp_app_with_users.post(
        "/dataset/register",
        headers=headers,
        data=json.dumps(dataset_info),
        content_type="application/json"
    )
    assert r.status_code == 401


def test_dataset_register_route_when_created_at_is_string(tmp_app_with_users):  # NOQA

    from dtool_lookup_server.utils import (
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

    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users.post(
        "/dataset/register",
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


def test_dataset_lookup_route(tmp_app_with_data):  # NOQA

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data.get(
        "/dataset/lookup/{}".format(uuid),
        headers=headers
    )
    assert r.status_code == 200

    assert len(json.loads(r.data.decode("utf-8"))) == 2

    r = tmp_app_with_data.get(
        "/dataset/lookup/{}".format(uuid),
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode("utf-8")) == []

    r = tmp_app_with_data.get(
        "/dataset/lookup/{}".format(uuid),
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401


def test_dataset_manifest_route(tmp_app_with_data):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"uri": "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"}
    r = tmp_app_with_data.post(
        "/dataset/manifest",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    expected_manifest = {
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
    }
    actual_manifest = json.loads(r.data.decode("utf-8"))

    assert expected_manifest == actual_manifest

    # Not authenticated, but in system.
    r = tmp_app_with_data.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + dopey_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    # Not authenticated, not in system.
    r = tmp_app_with_data.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + noone_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    # Not authorized.
    r = tmp_app_with_data.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 400

    # Base URI does not exist.
    query = {"uri": "s3://dontexist/af6727bf-29c7-43dd-b42f-a5d7ede28337"}
    r = tmp_app_with_data.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 400

    # URI does not exist.
    query = {"uri": "s3://snow-white/dontexist"}
    r = tmp_app_with_data.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 400

    # Broken query (no "uri").
    query = {"broken": "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"}
    r = tmp_app_with_data.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 422


def test_dataset_readme_route(tmp_app_with_data):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"uri": "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"}
    r = tmp_app_with_data.post(
        "/dataset/readme",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    expected_readme = "---\ndescripton: apples from queen"
    actual_readme = json.loads(r.data.decode("utf-8"))

    assert expected_readme == actual_readme


def test_dataset_annotations_route(tmp_app_with_data):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"uri": "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"}
    r = tmp_app_with_data.post(
        "/dataset/annotations",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    expected_readme = {"type": "fruit"}
    actual_readme = json.loads(r.data.decode("utf-8"))

    assert expected_readme == actual_readme
