"""Registration provenance: the server records which authenticated user
registered a dataset (uploaded_by/uploaded_at), as a server-asserted fact
separate from the client-claimed creator_username."""

import json
from urllib.parse import quote

UUID = "11111111-2222-4333-8444-555555555555"
BASE_URI = "s3://snow-white"
URI = f"{BASE_URI}/{UUID}"


def dataset_payload(**overrides):
    payload = {
        "uuid": UUID,
        "base_uri": BASE_URI,
        "uri": URI,
        "name": "provenance-test",
        "type": "dataset",
        "readme": "---\ndescription: provenance test",
        "manifest": {
            "dtoolcore_version": "3.18.0",
            "hash_function": "md5sum_hexdigest",
            "items": {},
        },
        "creator_username": "fr_lp1029",  # noisy machine-local claim
        "frozen_at": "1536238185.881941",
        "annotations": {},
        "tags": [],
    }
    payload.update(overrides)
    return payload


def register(client, token, payload):
    return client.put(
        f"/uris/{quote(URI, safe='')}",
        data=json.dumps(payload),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )


def test_register_via_api_records_authenticated_uploader(
        tmp_app_with_users_client, grumpy_token):  # NOQA
    from dservercore.sql_models import Dataset

    r = register(tmp_app_with_users_client, grumpy_token, dataset_payload())
    assert r.status_code == 201

    dataset = Dataset.query.filter_by(uri=URI).first()
    assert dataset is not None
    # creator_username keeps the client-side claim ...
    assert dataset.creator_username == "fr_lp1029"
    # ... while the server records who actually registered it.
    assert dataset.uploaded_by == "grumpy"
    assert dataset.uploaded_at is not None

    # Exposed in API responses (list datasets via empty search).
    r = tmp_app_with_users_client.post(
        "/uris",
        data=json.dumps({}),
        headers={
            "Authorization": f"Bearer {grumpy_token}",
            "Content-Type": "application/json",
        },
    )
    hits = [d for d in r.get_json() if d["uri"] == URI]
    assert len(hits) == 1
    assert hits[0]["uploaded_by"] == "grumpy"
    assert hits[0]["uploaded_at"] is not None


def test_register_without_request_context_leaves_uploader_empty(
        tmp_app_with_users):  # NOQA
    """CLI/indexer registrations run outside a JWT request context."""
    from dservercore.sql_models import Dataset
    from dservercore.utils import register_dataset

    register_dataset(dataset_payload(name="cli-registered"))

    dataset = Dataset.query.filter_by(uri=URI).first()
    assert dataset is not None
    assert dataset.uploaded_by is None


def test_client_cannot_forge_uploaded_by(
        tmp_app_with_users_client, grumpy_token):  # NOQA
    """uploaded_by is server-asserted; the register schema must reject it."""
    payload = dataset_payload(uploaded_by="mallory")
    r = register(tmp_app_with_users_client, grumpy_token, payload)
    assert r.status_code == 422


def test_search_filter_by_uploaded_by(
        tmp_app_with_users_client, grumpy_token):  # NOQA
    r = register(tmp_app_with_users_client, grumpy_token, dataset_payload())
    assert r.status_code == 201

    def search(query):
        r = tmp_app_with_users_client.post(
            "/uris",
            data=json.dumps(query),
            headers={
                "Authorization": f"Bearer {grumpy_token}",
                "Content-Type": "application/json",
            },
        )
        assert r.status_code == 200
        return r.get_json()

    hits = search({"uploaded_by": ["grumpy"]})
    assert len(hits) == 1
    assert hits[0]["uri"] == URI
    assert hits[0]["uploaded_by"] == "grumpy"

    assert search({"uploaded_by": ["someone-else"]}) == []


def test_summary_includes_uploader_facets(
        tmp_app_with_users_client, grumpy_token):  # NOQA
    r = register(tmp_app_with_users_client, grumpy_token, dataset_payload())
    assert r.status_code == 201

    r = tmp_app_with_users_client.get(
        "/me/summary",
        headers={"Authorization": f"Bearer {grumpy_token}"},
    )
    assert r.status_code == 200
    summary = r.get_json()
    assert "grumpy" in summary["uploaders"]
    assert summary["datasets_per_uploader"]["grumpy"] == 1
    assert summary["size_in_bytes_per_uploader"]["grumpy"] == 0
