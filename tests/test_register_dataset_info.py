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
    tmp_app.post(
        "/register_dataset_info",
        data=json.dumps(data),
        content_type='application/json'
    )

    lookup_url = "/lookup_dataset_info/{}".format(uuid)
    r = tmp_app.get(lookup_url)
    assert data == json.loads(r.data)
