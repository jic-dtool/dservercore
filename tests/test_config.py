"""Test the config module."""


def test_search_for_datasets_route(tmp_app_client):  # NOQA

    # Get the collection out of the tmp_app.
    assert tmp_app_client.application.config["SECRET_KEY"] is not None
