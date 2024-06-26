import pytest


def test_get_readme_from_uri_by_user(tmp_app_with_data_client):  # NOQA

    from dservercore import (
        AuthenticationError,
        AuthorizationError,
        UnknownBaseURIError,
        UnknownURIError,
    )
    from dservercore.utils import (
        get_readme_from_uri_by_user,
    )

    base_uri = "s3://snow-white"
    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)

    expected_readme = "---\ndescripton: apples from queen"

    assert get_readme_from_uri_by_user("grumpy", uri) == expected_readme

    with pytest.raises(AuthenticationError):
        get_readme_from_uri_by_user("dont_exist", uri)

    with pytest.raises(AuthorizationError):
        get_readme_from_uri_by_user("sleepy", uri)

    with pytest.raises(UnknownBaseURIError):
        get_readme_from_uri_by_user("grumpy", "s3://dont_exist/" + uuid)

    with pytest.raises(UnknownURIError):
        get_readme_from_uri_by_user("grumpy", base_uri + "/dont_exist")
