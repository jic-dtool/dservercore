"""Test the /datasets blueprint routes."""

import json

from . import tmp_app_with_data  # NOQA


def test_dataset_list_route(tmp_app_with_data):  # NOQA

    grumpy_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImdydW1weSJ9.lcFdRgucUyWXLrUApIp1s5c3B4zTtRHCX7SuFtgBpmAmF0cK6alUJIOazIHprIy2Df78PX45gNOhERo1uavlSAEL22FKoeHBFVB8xcea3UrETklM7n4pwew0djZoiPz7eUEhEwpVS5gdqFtmcFjaExmRODby8MBjGGpZ0FZabkVYTXAv0XKPouMjxFOEr0Ibuyqbm7gPlAakWNsxdA4M7emx9xM6OtYUPnDVwk3tSunvF4SBMlDC0whjw1ZTNBnURkC5BK2YSXli8c4LV_-Ww_CaTbxU4_Dw-KeRV2FJvccmQAUEXicz1VvTxtkDyBUTmd-R85K_lUSU4lwzW3dF0w"  # NOQA

    sleepy_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNsZWVweSJ9.N1BVpDBmxkmI0ONZisYgO-VsQNa3n3-7n3POYGY-mQTEYr-N3SIPI1_qjiOrc-y2GT8VIvs4mxVWwRPesW24F7_W5_vhwHwD_YlnloBGpk03GL84qX06GK12uo8Ajyclt4OzVE4XCwxUzPtgH6PhVIo5VdwKZfxbt3eBJyAYtX6s6Bu-C61kI33TnBi-sLeZawWTibvOGZmBuLeldlJoek5npjoM2Ck4-FR4MLPbwQS8cIJzKjYbpgJh2DMbHV_Yqa4jl89nuzG8a-1I2PmXognNdzwP2RKNDnZwd2oMEl7HJ7WkgqOyyPBz3X4ZAEwEpzo7hESNgdrByF_igMA67Q"  # NOQA

    dopey_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImRvcGV5In0.apbGUn4u8v4nnHr3jw2ggnBfZf1Gc2tgK4hFYQ_tLK9sFozHgP6vjmBBzXTlYpZcnco8TWjIWSSU3PfoF5cXUvjh9ZY19FjiT0AQXQgHiVylNn2Ou1G0t1M71Y6nA_t8mKsyA4YbQ-OCM8I04JXPyGvN3xnK_d3JF-j8RHCS2i3_w9iPuBsns92NSxvkxkWSWIa00BsYTHaVWFWY9gCPaNP5I6VGR-o0TDlAtOrGmzMkBhTsgmeUpg2alLJ4CHX8c4Y0iefayM2UcBwW2dm8oUQf8pKAVM0iFF1ztivh-hocMYM5kb7UuhqB35x0uLaf24nm1d11kYbi0FizjAAG-w"  # NOQA

    r = tmp_app_with_data.post(
        "/dataset/list",
        data=json.dumps(dict(token=grumpy_token)),
        content_type="application/json"
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

    r = tmp_app_with_data.post(
        "/dataset/list",
        data=json.dumps(dict(token=sleepy_token)),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert json.loads(r.data) == []

    r = tmp_app_with_data.post(
        "/dataset/list",
        data=json.dumps(dict(token=dopey_token)),
        content_type="application/json"
    )
    assert r.status_code == 401
