"""Test registering of datasets."""

import json

from . import tmp_app  # NOQA


def test_register_dataset(tmp_app):  # NOQA

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    data = {
        "uuid": uuid,
        "type": "dataset",
        "uri": "file:///tmp/a_dataset"
    }
    r = tmp_app.post(
        "/register_dataset",
        data=json.dumps(data),
        content_type='application/json'
    )

    assert r.status_code == 200

    lookup_url = "/lookup_datasets/{}".format(uuid)
    r = tmp_app.get(lookup_url)
    assert [data] == json.loads(r.data)


def test_register_dataset_raises_bad_request_when_dataset_info_is_invalid(tmp_app):  # NOQA
    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    data = {
        "uuid": uuid,
        "type": "protodataset",
        "uri": "file:///tmp/a_dataset"
    }

    r = tmp_app.post(
        "/register_dataset",
        data=json.dumps(data),
        content_type='application/json'
    )

    assert r.status_code == 400
