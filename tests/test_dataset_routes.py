"""Test the /datasets blueprint routes."""

import json

from . import tmp_app_with_data  # NOQA

def test_dataset_list_route(tmp_app_with_data):  # NOQA

    grumpy_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImdydW1weSJ9.lcFdRgucUyWXLrUApIp1s5c3B4zTtRHCX7SuFtgBpmAmF0cK6alUJIOazIHprIy2Df78PX45gNOhERo1uavlSAEL22FKoeHBFVB8xcea3UrETklM7n4pwew0djZoiPz7eUEhEwpVS5gdqFtmcFjaExmRODby8MBjGGpZ0FZabkVYTXAv0XKPouMjxFOEr0Ibuyqbm7gPlAakWNsxdA4M7emx9xM6OtYUPnDVwk3tSunvF4SBMlDC0whjw1ZTNBnURkC5BK2YSXli8c4LV_-Ww_CaTbxU4_Dw-KeRV2FJvccmQAUEXicz1VvTxtkDyBUTmd-R85K_lUSU4lwzW3dF0w"  # NOQA


    r = tmp_app_with_data.post(
        "/dataset/list",
        data=json.dumps(dict(token=grumpy_token)),
        content_type="application/json"
    )
    assert r.status_code == 200
