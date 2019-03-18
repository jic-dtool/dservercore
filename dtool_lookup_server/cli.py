"""Command line utility functions."""

import sys

import click
from flask import Flask
import jwt

from dtool_lookup_server.utils import (
    _get_user_obj,
    _get_base_uri_obj,
    register_users,
    register_base_uri,
    show_permissions,
    update_permissions,
)

app = Flask(__name__)


@app.cli.command()
@click.argument('username')
@click.option('-a', '--is_admin', is_flag=True)
def register_user(username, is_admin):
    """Register a user in the dtool lookup server."""

    if _get_user_obj(username) is not None:
        click.secho(
            "User '{}' already registered".format(username),
            fg="red",
            err=True
        )
        sys.exit(1)

    users = [{
        "username": username,
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


@app.cli.command()
@click.argument('base_uri')
@click.argument('username')
def give_search_permission(base_uri, username):
    """Give a user search permission on a base URI."""

    if _get_base_uri_obj(base_uri) is None:
        click.secho(
            "Base URI '{}' not registered".format(base_uri),
            fg="red",
            err=True
        )
        sys.exit(1)

    if _get_user_obj(username) is None:
        click.secho(
            "User '{}' not registered".format(username),
            fg="red",
            err=True
        )
        sys.exit(1)

    permissions = show_permissions(base_uri)

    if username in permissions["users_with_search_permissions"]:
        click.secho(
            "User '{}' already has search permissions".format(username),
            fg="red",
            err=True
        )
        sys.exit(1)

    permissions["users_with_search_permissions"].append(username)
    update_permissions(permissions)


@app.cli.command()
@click.argument('private-key-file', type=click.Path(exists=True, dir_okay=False))
@click.argument('username')
def generate_token(private_key_file, username):
    """Generate a token for a user in the dtool lookup server."""

    if _get_user_obj(username) is None:
        click.secho(
            "User '{}' not registered".format(username),
            fg="red",
            err=True
        )
        sys.exit(1)

    private_key = open(private_key_file, "r").read()

    token = jwt.encode(
        {'username': username},
        private_key,
        algorithm='RS256')
    click.secho(token.decode("utf-8"))
