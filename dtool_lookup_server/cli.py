"""Command line utility functions."""

import sys

import click
from flask import Flask

from dtool_lookup_server.utils import (
    _get_user_obj,
    _get_base_uri_obj,
    register_users,
    register_base_uri,
)

app = Flask(__name__)


@app.cli.command()
@click.argument('name')
@click.option('-a', '--is_admin', is_flag=True)
def register_user(name, is_admin):
    """Register a user in the dtool lookup server."""

    if _get_user_obj(name) is not None:
        click.secho(
            "User '{}' already registered".format(name),
            fg="red",
            err=True
        )
        sys.exit(1)

    users = [{
        "username": name,
        "is_admin": is_admin
    }]
    register_users(users)


@app.cli.command()
@click.argument('base_uri')
def add_base_uri(base_uri):
    """Register a base URI in the dtool lookup server."""

    if _get_base_uri_obj(base_uri) is not None:
        click.secho(
            "Base URI '{}' already registered".format(base_uri),
            fg="red",
            err=True
        )
        sys.exit(1)

    register_base_uri(base_uri)
