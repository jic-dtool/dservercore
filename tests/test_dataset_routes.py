"""Test the /datasets blueprint routes."""

import json

from . import tmp_app_with_data  # NOQA


def test_dataset_list_route(tmp_app_with_data):  # NOQA

    grumpy_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5NjJjODEyNi1kZDJlLTQ1NDEtODQyOC0yZDYxYjEwZmU0M2YiLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU1MzIyMzEzMywidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU1MzIyMzEzMywiaWRlbnRpdHkiOiJncnVtcHkifQ.K1YYcUp2jfpBhVd7ggBJ_mpnQT_ZAGRjfgrReoz9no6zZ_5Hlgq2YLUNFtFfr2PrqsaO5fKWUfKrR8bjMijtlRlAEmyCJvalqXDWvriMf2QowyR6IjKxSNZcVCMkJXEk7cRlEM9f815YABc3RsG1F75n2dV5NSuvcQ4dQoItvNYpsuHZ3c-xYQuaQt7_Ch50Ez-H2fJatXQYdnHruyZOJQKPIssxU_yyeCnlOGklCmDn8mIolQEChrvW9HhpvgXsaAWEHjtNRK4T_ZH37Dq44fIB9ax6GGRZHDjWmjOicrGolfu73BuI8fOpLLpW5af6SKP-UhZA4AcW_TYG4PnOpQ"  # NOQA

    sleepy_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhNzBhNmQ1ZS0xMTU4LTQ5YzAtOGM0OS02MmU1MzYzZWM3NDQiLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU1MzIyMzIyNCwidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU1MzIyMzIyNCwiaWRlbnRpdHkiOiJzbGVlcHkifQ.o15vGkZVsP_RaCIwXljFrkmFTef7ToPo_ssg7DPzRc33LhZh352gn6kY90JGMD1eyvrw69u6RwKW_5RkBmkDweCExiSDx7EuEofgadEegkM9qfbRfPGRpihobmQmwDADc6qspROUDi__gjrALLFZvg8cAteBVOBhKrItwHADym4RCHzDTyP0dd-k8PzvKUqBxryK5yutpc5Tkju3Bg33bFIyjJTr9kzZbjnzoYSjl1Nb7YtCO6ijsJasIPfLK8OOB2kza9NrAOAhWKqWtynzkyCCVckicfGZI5ywzNlsUqGcQwb7fNMUR-1JErM0wGViKOmotcQ08ut69KM5p8XZmg"  # NOQA

    dopey_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI0MTIxZDhhYi1iYjg5LTRlYTgtOTg3Zi0zYjgyOTc2ODkwZjEiLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU1MzIyMzM0MCwidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU1MzIyMzM0MCwiaWRlbnRpdHkiOiJkb3BleSJ9.K8MeDodbdwDN2ErspmWgQJCra3EXdpIrsyWQVqCNZNKsjUZsYLNAetzqJe71NhiVFuoaqDm0ta9jNnQE5NpehQSFv0SveMPu4wIaVpcCDQXHOYGGljbhHa18v0dEZibZFEYnMwY_b0VWtpzXZXZSYiLVMD2kcnUqXouV7fPXlSp5SuFCEh5Y6rw0nZqxMTVdbDvZLm2rxjJI_4GHMj1KMpsGKYGTxniA1iWvR9WionJOdDxn5gc8roDERGuSQpm4LCQxz_WJk8pNX4IdQgPuz6TVNsXnUnD2LiGe9Dz8q-FstcTwRy2u97l76OgCGSf7vkhELHTqRj32cEdxnPNpTA"  # NOQA


    headers=dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_data.get(
        "/dataset/list",
        headers=headers
    )
    assert r.status_code == 200

    expected_content = []
    for base_uri in ["s3://snow-white", "s3://mr-men"]:
        uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
        uri = "{}/{}".format(base_uri, uuid)
        expected_content.append({
            "base_uri": base_uri,
            "uuid": uuid,
            "uri": uri,
            "name": "bad-apples"
        })
    assert json.loads(r.data) == expected_content

    r = tmp_app_with_data.get(
        "/dataset/list",
        headers=dict(Authorization="Bearer " + sleepy_token)
    )
    assert r.status_code == 200
    assert json.loads(r.data) == []

    r = tmp_app_with_data.get(
        "/dataset/list",
        headers=dict(Authorization="Bearer " + dopey_token)
    )
    assert r.status_code == 401
