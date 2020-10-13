"""Test the /config blueprint routes."""

import json
import dtool_lookup_server

from . import tmp_app_with_users  # NOQA

snowwhite_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyZTk0MzMzMi0wZWE5LTQ3MWMtYTUxZS02MjUxNGNlOTdkOGMiLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU1MzI2NTM5NywidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU1MzI2NTM5NywiaWRlbnRpdHkiOiJzbm93LXdoaXRlIn0.FAoj9M4Tpr9IXIsyuD9eKV3oOpQ4_oRE82v6jqMFOSERaMqfWQgpMlTPSBsoWvnsNhigBYA7NKqqRPZ_bCHh73dMk57s6-VBvxtunQIe-MYtnOP9H4lpIdnceIE-Ji34xCd7kxIp0kADtYLhnJjU6Jesk642P0Ndjc8ePxGAl-l--bLbH_A4a3-U2EuowBSwqAp2q56QuGw6oQpKSKt9_eRSThNBE6zJIClfUeQYeCDCcd1Inh5hgrDBurteicCP8gWyVkyZ0YnjojDMECu7P9vDyy-T4AUem9EIAe_hA1nTMKucW2Ki6xyZLvu0TVlHe9AQVYy0O-suxxlrXIJ5Yw"  # NOQA

grumpy_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5NjJjODEyNi1kZDJlLTQ1NDEtODQyOC0yZDYxYjEwZmU0M2YiLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU1MzIyMzEzMywidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU1MzIyMzEzMywiaWRlbnRpdHkiOiJncnVtcHkifQ.K1YYcUp2jfpBhVd7ggBJ_mpnQT_ZAGRjfgrReoz9no6zZ_5Hlgq2YLUNFtFfr2PrqsaO5fKWUfKrR8bjMijtlRlAEmyCJvalqXDWvriMf2QowyR6IjKxSNZcVCMkJXEk7cRlEM9f815YABc3RsG1F75n2dV5NSuvcQ4dQoItvNYpsuHZ3c-xYQuaQt7_Ch50Ez-H2fJatXQYdnHruyZOJQKPIssxU_yyeCnlOGklCmDn8mIolQEChrvW9HhpvgXsaAWEHjtNRK4T_ZH37Dq44fIB9ax6GGRZHDjWmjOicrGolfu73BuI8fOpLLpW5af6SKP-UhZA4AcW_TYG4PnOpQ"  # NOQA

noone_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhMzUwY2MwZS1jMzAyLTQ1MGItYTE0NC01YTQzZjE3MDc4NDkiLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU1MzI3NzA1MCwidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU1MzI3NzA1MCwiaWRlbnRpdHkiOiJub29uZSJ9.VCRRsfLM5mwYz_viMVAJzfLf3_IF7MDTyzeWv3Ae_YYumu3UQVXUqWqJnvwyAY7KAqEIWkoFUET_bp-48WrvGaGr8q355IXiqspURpMMCLQ4G7Jwm3EnN6I61e_C6XpoyliZnd06qiVZR5VuaHxk41XclwRwgPCsEflj30SKWgVQOGbOYFfcSEdMKUvu8fyGbRwo47ynHvHrmxMAuURWjnN3g8gD-shBHCt1_4GVDSp1LSipSysDcn3-SdFa0PLGZqQ4Xj7QzM7AMmZ20J0uSHVA5U6RBzLU8d_neDdAg-Y2sjAC_G2P7jj0RdIU-QlDx2B25nyr4rOO9oSOI_q54Q"  # NOQA


def test_config_info_route(tmp_app_with_users):  # NOQA

    headers = dict(Authorization="Bearer " + snowwhite_token)
    r = tmp_app_with_users.get(
        "/config/info",
        headers=headers,
    )
    assert r.status_code == 200

    # NOTE: If the configuration grows in the future, this text must adapt or will fail otherwise.
    expected_content = {
        'jsonify_prettyprint_regular': True,
        'jwt_algorithm': 'RS256',
        'jwt_header_name': 'Authorization',
        'jwt_header_type': 'Bearer',
        'jwt_public_key': '',
        'jwt_token_location': 'headers',
        'sqlalchemy_track_modifications': False,
        'version': dtool_lookup_server.__version__}

    response = json.loads(r.data.decode("utf-8"))

    # this allows the test to succeed if more config options enter in the future
    for k, v in expected_content.items():
        assert k in response
        if k == "jwt_public_key":
            # Ignore the value of the public key.
            continue
        assert v == response[k]


def test_config_info_route_authorization(tmp_app_with_users):  # NOQA

    # All users in the system should have access to the /config route.
    # For example "snow-white" and "grumpy"
    for t in (snowwhite_token, grumpy_token):
        headers = dict(Authorization="Bearer " + snowwhite_token)
        r = tmp_app_with_users.get(
            "/config/info",
            headers=headers,
        )
        assert r.status_code == 200

    # However a user that is not registered in the system should get 401.
    headers = dict(Authorization="Bearer " + noone_token)
    r = tmp_app_with_users.get(
        "/config/info",
        headers=headers,
    )
    assert r.status_code == 401
