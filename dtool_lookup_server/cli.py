"""Command line utility functions."""

import sys

import click
from flask import Flask

from dtool_lookup_server.utils import (
    _get_user_obj,
    register_users,
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
