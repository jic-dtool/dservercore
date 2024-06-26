"""Test the /manifest, /readme, /annotations, /tags blueprint routes."""

import json

from dservercore.utils import uri_to_url_suffix


def test_dataset_manifest_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    uri = "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)
    r = tmp_app_with_data_client.get(
        f"/manifests/{url_suffix}",
        headers=headers
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
    r = tmp_app_with_data_client.get(
        f"/manifests/{url_suffix}",
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401

    # Not authenticated, not in system.
    r = tmp_app_with_data_client.get(
        f"/manifests/{url_suffix}",
        headers=dict(Authorization="Bearer " + noone_token)
    )
    assert r.status_code == 401

    # Not authorized.
    r = tmp_app_with_data_client.get(
        f"/manifests/{url_suffix}",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 403

    # Not authorized and base URI does not exist.
    uri = "s3://dontexist/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/manifests/{url_suffix}",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 403

    # Authorized and base URI does not exist.
    uri = "s3://dontexist/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/manifests/{url_suffix}",
        headers=dict(Authorization="Bearer " + grumpy_token)
    )
    assert r.status_code == 403

    # URI does not exist.
    uri = "s3://snow-white/dontexist"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/manifests/{url_suffix}",
        headers=dict(Authorization="Bearer " + grumpy_token)
    )
    assert r.status_code == 404


def test_dataset_readme_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    uri = "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/readmes/{url_suffix}",
        headers=headers
    )
    assert r.status_code == 200

    expected_readme = {"readme": "---\ndescripton: apples from queen"}
    actual_readme = json.loads(r.data.decode("utf-8"))

    assert expected_readme == actual_readme

    # Not authenticated, but in system.
    r = tmp_app_with_data_client.get(
        f"/readmes/{url_suffix}",
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401

    # Not authenticated, not in system.
    r = tmp_app_with_data_client.get(
        f"/readmes/{url_suffix}",
        headers=dict(Authorization="Bearer " + noone_token)
    )
    assert r.status_code == 401

    # Not authorized.
    r = tmp_app_with_data_client.get(
        f"/readmes/{url_suffix}",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 403

    # Not authorized and base URI does not exist.
    uri = "s3://dontexist/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/readmes/{url_suffix}",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 403

    # Authorized and base URI does not exist.
    uri = "s3://dontexist/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/readmes/{url_suffix}",
        headers=dict(Authorization="Bearer " + grumpy_token)
    )
    assert r.status_code == 403

    # Authorized and base URI does exist, but dataset URI does not exist.
    uri = "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28339"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/readmes/{url_suffix}",
        headers=dict(Authorization="Bearer " + grumpy_token)
    )
    assert r.status_code == 404


def test_dataset_annotations_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    uri = "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/annotations/{url_suffix}",
        headers=headers
    )
    assert r.status_code == 200

    expected_annotations = {"annotations": {"type": "fruit"}}
    actual_annotations = json.loads(r.data.decode("utf-8"))

    assert expected_annotations == actual_annotations

    # Not authenticated, but in system.
    r = tmp_app_with_data_client.get(
        f"/annotations/{url_suffix}",
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401

    # Not authenticated, not in system.
    r = tmp_app_with_data_client.get(
        f"/annotations/{url_suffix}",
        headers=dict(Authorization="Bearer " + noone_token)
    )
    assert r.status_code == 401

    # Not authorized.
    r = tmp_app_with_data_client.get(
        f"/annotations/{url_suffix}",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 403

    # Not authorized and base URI does not exist.
    uri = "s3://dontexist/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/annotations/{url_suffix}",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 403

    # Authorized and base URI does not exist.
    uri = "s3://dontexist/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/annotations/{url_suffix}",
        headers=dict(Authorization="Bearer " + grumpy_token)
    )
    assert r.status_code == 403

    # Authorized and base URI does exist, but dataset URI does not exist.
    uri = "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28339"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/annotations/{url_suffix}",
        headers=dict(Authorization="Bearer " + grumpy_token)
    )
    assert r.status_code == 404


def test_dataset_tags_route(
        tmp_app_with_data_client,
        grumpy_token,
        sleepy_token,
        dopey_token,
        noone_token):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)
    uri = "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/tags/{url_suffix}",
        headers=headers
    )
    assert r.status_code == 200

    expected_tags = {"tags": ['evil', 'fruit']}
    actual_tags = json.loads(r.data.decode("utf-8"))

    assert expected_tags == actual_tags

    # Not authenticated, but in system.
    r = tmp_app_with_data_client.get(
        f"/tags/{url_suffix}",
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401

    # Not authenticated, not in system.
    r = tmp_app_with_data_client.get(
        f"/tags/{url_suffix}",
        headers=dict(Authorization="Bearer " + noone_token)
    )
    assert r.status_code == 401

    # Not authorized.
    r = tmp_app_with_data_client.get(
        f"/tags/{url_suffix}",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 403

    # Not authorized and base URI does not exist.
    uri = "s3://dontexist/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/tags/{url_suffix}",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 403

    # Authorized and base URI does not exist.
    uri = "s3://dontexist/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/tags/{url_suffix}",
        headers=dict(Authorization="Bearer " + grumpy_token)
    )
    assert r.status_code == 403

    # Authorized and base URI does exist, but dataset URI does not exist.
    uri = "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28339"
    url_suffix = uri_to_url_suffix(uri)

    r = tmp_app_with_data_client.get(
        f"/tags/{url_suffix}",
        headers=dict(Authorization="Bearer " + grumpy_token)
    )
    assert r.status_code == 404
