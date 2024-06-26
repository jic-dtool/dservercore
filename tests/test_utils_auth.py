"""Test the auth utils."""

from dservercore.utils_auth import (
    user_exists,
    has_admin_rights,
    may_search,
    may_register,
    list_search_base_uris,
    list_register_base_uris,
)


def test_user_exists(tmp_app_with_users_client):  # NOQA
    assert user_exists("snow-white")
    assert user_exists("grumpy")
    assert not user_exists("dontexist")


def test_has_admin_rights(tmp_app_with_users_client):  # NOQA
    assert has_admin_rights("snow-white")
    assert not has_admin_rights("grumpy")
    assert not has_admin_rights("dontexist")


def test_may_search(tmp_app_with_users_client):  # NOQA
    assert may_search("grumpy", "s3://snow-white")
    assert not may_search("snow-white", "s3://snow-white")
    assert not may_search("dontexist", "s3://snow-white")
    assert not may_search("grumpy", "s3://dontexist")


def test_may_register(tmp_app_with_users_client):  # NOQA
    assert may_register("grumpy", "s3://snow-white")
    assert not may_register("sleepy", "s3://snow-white")
    assert not may_register("dontexist", "s3://snow-white")
    assert not may_register("grumpy", "s3://dontexist")


def test_list_search_base_uris(tmp_app_with_users_client):  # NOQA
    assert list_search_base_uris("snow-white") == []
    assert list_search_base_uris("grumpy") == ["s3://snow-white"]
    assert list_search_base_uris("dontexist") == []


def test_list_register_base_uris(tmp_app_with_users_client):  # NOQA
    assert list_register_base_uris("sleepy") == []
    assert list_register_base_uris("grumpy") == ["s3://snow-white"]
    assert list_register_base_uris("dontexist") == []
