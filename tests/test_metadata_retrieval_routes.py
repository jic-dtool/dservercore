"""Test the /manifest, /readme, /annotations blueprint routes."""

import json


def test_dataset_manifest_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"uri": "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"}
    r = tmp_app_with_data_client.post(
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
    r = tmp_app_with_data_client.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + dopey_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    # Not authenticated, not in system.
    r = tmp_app_with_data_client.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + noone_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    # Not authorized.
    r = tmp_app_with_data_client.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 400

    # Base URI does not exist.
    query = {"uri": "s3://dontexist/af6727bf-29c7-43dd-b42f-a5d7ede28337"}
    r = tmp_app_with_data_client.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 400

    # URI does not exist.
    query = {"uri": "s3://snow-white/dontexist"}
    r = tmp_app_with_data_client.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 400

    # Broken query (no "uri").
    query = {"broken": "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"}
    r = tmp_app_with_data_client.post(
        "/dataset/manifest",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 422


def test_dataset_readme_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"uri": "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"}
    r = tmp_app_with_data_client.post(
        "/dataset/readme",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    expected_readme = "---\ndescripton: apples from queen"
    actual_readme = json.loads(r.data.decode("utf-8"))

    assert expected_readme == actual_readme


def test_dataset_annotations_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    query = {"uri": "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"}
    r = tmp_app_with_data_client.post(
        "/dataset/annotations",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    expected_readme = {"type": "fruit"}
    actual_readme = json.loads(r.data.decode("utf-8"))

    assert expected_readme == actual_readme
