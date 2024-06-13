import pytest


def test_get_manifest_from_uri_by_user(tmp_app_with_data_client):  # NOQA

    from dservercore import (
        AuthenticationError,
        AuthorizationError,
        UnknownBaseURIError,
        UnknownURIError,
    )
    from dservercore.utils import (
        get_manifest_from_uri_by_user,
    )

    base_uri = "s3://snow-white"
    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)

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

    assert get_manifest_from_uri_by_user("grumpy", uri) == expected_manifest

    with pytest.raises(AuthenticationError):
        get_manifest_from_uri_by_user("dont_exist", uri)

    with pytest.raises(AuthorizationError):
        get_manifest_from_uri_by_user("sleepy", uri)

    with pytest.raises(UnknownBaseURIError):
        get_manifest_from_uri_by_user("grumpy", "s3://dont_exist/" + uuid)

    with pytest.raises(UnknownURIError):
        get_manifest_from_uri_by_user("grumpy", base_uri + "/dont_exist")
