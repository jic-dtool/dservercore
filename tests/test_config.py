"""Test the config module."""

from . import tmp_app  # NOQA


def test_search_for_datasets_route(tmp_app):  # NOQA

    # Get the collection out of the tmp_app.
    assert tmp_app.application.config["SECRET_KEY"] is not None
