"""Audit regression test: PUT /readmes must map missing register
permission to 403, not crash with an uncaught AuthorizationError (500)."""

from urllib.parse import quote


def test_set_readme_without_register_permission_403(
        tmp_app_with_users_client, sleepy_token):  # NOQA
    """sleepy has search but not register permission on s3://snow-white."""
    uri = "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    response = tmp_app_with_users_client.put(
        f"/readmes/{quote(uri, safe='')}",
        json={"readme": "---\nproject: hijack"},
        headers={"Authorization": f"Bearer {sleepy_token}"},
    )
    assert response.status_code == 403


def test_set_readme_unregistered_user_401(
        tmp_app_with_users_client, noone_token):  # NOQA
    uri = "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337"
    response = tmp_app_with_users_client.put(
        f"/readmes/{quote(uri, safe='')}",
        json={"readme": "---\nproject: x"},
        headers={"Authorization": f"Bearer {noone_token}"},
    )
    assert response.status_code == 401
