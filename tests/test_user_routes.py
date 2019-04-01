"""Test the /user blueprint routes."""

import json

from . import tmp_app_with_users  # NOQA

snowwhite_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyZTk0MzMzMi0wZWE5LTQ3MWMtYTUxZS02MjUxNGNlOTdkOGMiLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU1MzI2NTM5NywidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU1MzI2NTM5NywiaWRlbnRpdHkiOiJzbm93LXdoaXRlIn0.FAoj9M4Tpr9IXIsyuD9eKV3oOpQ4_oRE82v6jqMFOSERaMqfWQgpMlTPSBsoWvnsNhigBYA7NKqqRPZ_bCHh73dMk57s6-VBvxtunQIe-MYtnOP9H4lpIdnceIE-Ji34xCd7kxIp0kADtYLhnJjU6Jesk642P0Ndjc8ePxGAl-l--bLbH_A4a3-U2EuowBSwqAp2q56QuGw6oQpKSKt9_eRSThNBE6zJIClfUeQYeCDCcd1Inh5hgrDBurteicCP8gWyVkyZ0YnjojDMECu7P9vDyy-T4AUem9EIAe_hA1nTMKucW2Ki6xyZLvu0TVlHe9AQVYy0O-suxxlrXIJ5Yw"  # NOQA

grumpy_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5NjJjODEyNi1kZDJlLTQ1NDEtODQyOC0yZDYxYjEwZmU0M2YiLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU1MzIyMzEzMywidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU1MzIyMzEzMywiaWRlbnRpdHkiOiJncnVtcHkifQ.K1YYcUp2jfpBhVd7ggBJ_mpnQT_ZAGRjfgrReoz9no6zZ_5Hlgq2YLUNFtFfr2PrqsaO5fKWUfKrR8bjMijtlRlAEmyCJvalqXDWvriMf2QowyR6IjKxSNZcVCMkJXEk7cRlEM9f815YABc3RsG1F75n2dV5NSuvcQ4dQoItvNYpsuHZ3c-xYQuaQt7_Ch50Ez-H2fJatXQYdnHruyZOJQKPIssxU_yyeCnlOGklCmDn8mIolQEChrvW9HhpvgXsaAWEHjtNRK4T_ZH37Dq44fIB9ax6GGRZHDjWmjOicrGolfu73BuI8fOpLLpW5af6SKP-UhZA4AcW_TYG4PnOpQ"  # NOQA

noone_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhMzUwY2MwZS1jMzAyLTQ1MGItYTE0NC01YTQzZjE3MDc4NDkiLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU1MzI3NzA1MCwidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU1MzI3NzA1MCwiaWRlbnRpdHkiOiJub29uZSJ9.VCRRsfLM5mwYz_viMVAJzfLf3_IF7MDTyzeWv3Ae_YYumu3UQVXUqWqJnvwyAY7KAqEIWkoFUET_bp-48WrvGaGr8q355IXiqspURpMMCLQ4G7Jwm3EnN6I61e_C6XpoyliZnd06qiVZR5VuaHxk41XclwRwgPCsEflj30SKWgVQOGbOYFfcSEdMKUvu8fyGbRwo47ynHvHrmxMAuURWjnN3g8gD-shBHCt1_4GVDSp1LSipSysDcn3-SdFa0PLGZqQ4Xj7QzM7AMmZ20J0uSHVA5U6RBzLU8d_neDdAg-Y2sjAC_G2P7jj0RdIU-QlDx2B25nyr4rOO9oSOI_q54Q"  # NOQA


def test_list_user_route(tmp_app_with_users):  # NOQA

    # Snow-white admin retrieve's her own info.
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.get(
        "/user/info/snow-white",
        headers=headers,
    )
    assert r.status_code == 200

    expected_content = {
        u"username": u"snow-white",
        u"is_admin": True,
        u"search_permissions_on_base_uris": [],
        u"register_permissions_on_base_uris": []
    }
    assert json.loads(r.data.decode("utf-8")) == expected_content

    # Grumpy non-admin retrieve's his own info.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users.get(
        "/user/info/grumpy",
        headers=headers,
    )
    assert r.status_code == 200

    base_uri = "s3://snow-white"
    expected_content = {
        u"username": u"grumpy",
        u"is_admin": False,
        u"search_permissions_on_base_uris": [base_uri],
        u"register_permissions_on_base_uris": [base_uri]
    }
    assert json.loads(r.data) == expected_content

    # Snow-white admin retrieve Grumpy's info.
    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.get(
        "/user/info/grumpy",
        headers=headers,
    )
    assert r.status_code == 200

    base_uri = "s3://snow-white"
    expected_content = {
        u"username": u"grumpy",
        u"is_admin": False,
        u"search_permissions_on_base_uris": [base_uri],
        u"register_permissions_on_base_uris": [base_uri]
    }
    assert json.loads(r.data) == expected_content

    # Noone tries to retrieve Grumpy's info. 404.
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users.get(
        "/user/info/grumpy",
        headers=headers,
    )
    assert r.status_code == 404

    # Grumpy tries to retrieve Snow White's info. 404.
    headers = dict(Authorization="Bearer " + grumpy_token)
    r = tmp_app_with_users.get(
        "/user/info/snow-white",
        headers=headers,
    )
    assert r.status_code == 404
