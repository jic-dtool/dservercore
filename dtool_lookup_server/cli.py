"""Command line utility functions."""

import os
import sys

import click
from flask import Flask
from flask_jwt_extended import create_access_token

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
@click.argument('base_uri')
@click.argument('username')
def give_register_permission(base_uri, username):
    """Give a user register permission on a base URI."""

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

    if username in permissions["users_with_register_permissions"]:
        click.secho(
            "User '{}' already has register permissions".format(username),
            fg="red",
            err=True
        )
        sys.exit(1)

    permissions["users_with_register_permissions"].append(username)
    update_permissions(permissions)


@app.cli.command()
@click.argument('username')
@click.option("--last-forever", is_flag=True)
def generate_token(username, last_forever):
    """Generate a token for a user in the dtool lookup server."""

    if _get_user_obj(username) is None:
        click.secho(
            "User '{}' not registered".format(username),
            fg="red",
            err=True
        )
        sys.exit(1)

    if last_forever:
        token = create_access_token(identity=username, expires_delta=False)
    else:
        token = create_access_token(identity=username)
    click.secho(token.decode("utf-8"))
