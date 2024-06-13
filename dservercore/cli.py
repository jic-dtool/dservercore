"""Command line utility functions."""

import json
import sys

import click
import dtoolcore
import dtoolcore.utils
from flask import Flask, current_app
from flask.cli import AppGroup
from flask_jwt_extended import create_access_token

from dtoolcore import iter_datasets_in_base_uri, DataSet
import dservercore
import dservercore.utils
from dservercore.utils import (
    base_uri_exists,
    user_exists,
    delete_users,
    register_users,
    update_users,
    register_base_uri,
    get_permission_info,
    register_permissions,
    register_dataset,
    generate_dataset_info,
    obj_to_dict,
    versions_to_dict
)
from dservercore.config import CONFIG_EXCLUSIONS

app = Flask(__name__)

user_cli = AppGroup("user", help="User management commands.")
base_uri_cli = AppGroup("base_uri", help="Base URI management commands.")
dataset_cli = AppGroup("dataset", help="Dataset index management commands.")
config_cli = AppGroup("config", help="Config inspection commands.")


@user_cli.command(name="add")
@click.argument("username")
@click.option("-a", "--is_admin", is_flag=True)
def register_user(username, is_admin):
    """Register a user in dserver."""

    if user_exists(username):
        click.secho("User '{}' already registered".format(username), fg="red", err=True)
        sys.exit(1)

    users = [{"username": username, "is_admin": is_admin}]
    register_users(users)


@user_cli.command(name="update")
@click.argument("username")
@click.option("-a", "--is_admin", is_flag=True)
def update_user(username, is_admin):
    """Update a user in dserver."""

    if not user_exists(username):
        click.secho(
            "User '{}' is not registered yet".format(username), fg="red", err=True
        )
        sys.exit(1)

    users = [{"username": username, "is_admin": is_admin}]
    update_users(users)


@user_cli.command(name="delete")
@click.argument("username")
def delete_user(username):
    """Delete a user in dserver."""
    users = [
        {
            "username": username,
        }
    ]
    delete_users(users)


@user_cli.command(name="list")
def list_users():
    """List the users in dserver."""
    click.secho(json.dumps(dservercore.utils.list_users(), indent=2))


@base_uri_cli.command(name="add")
@click.argument("base_uri")
def add_base_uri(base_uri):
    """Register a base URI in dserver."""
    base_uri = dtoolcore.utils.sanitise_uri(base_uri)
    if base_uri_exists(base_uri):
        click.secho(
            "Base URI '{}' already registered".format(base_uri), fg="red", err=True
        )
        sys.exit(1)

    register_base_uri(base_uri)


@base_uri_cli.command(name="list")
def list_base_uris():
    """List the base URIs in dserver."""
    click.secho(json.dumps(dservercore.utils.list_base_uris(), indent=2))


@user_cli.command(name="search_permission")
@click.argument("username")
@click.argument("base_uri")
def give_search_permission(username, base_uri):
    """Give a user search permission on a base URI."""

    if not base_uri_exists(base_uri):
        click.secho("Base URI '{}' not registered".format(base_uri), fg="red", err=True)
        sys.exit(1)

    if not user_exists(username):
        click.secho("User '{}' not registered".format(username), fg="red", err=True)
        sys.exit(1)

    permissions = get_permission_info(base_uri)

    if username in permissions["users_with_search_permissions"]:
        click.secho(
            "User '{}' already has search permissions".format(username),
            fg="red",
            err=True,
        )
        sys.exit(1)

    permissions["users_with_search_permissions"].append(username)
    register_permissions(base_uri, permissions)


@user_cli.command(name="register_permission")
@click.argument("username")
@click.argument("base_uri")
def give_register_permission(username, base_uri):
    """Give a user register permission on a base URI."""

    if not base_uri_exists(base_uri):
        click.secho("Base URI '{}' not registered".format(base_uri), fg="red", err=True)
        sys.exit(1)

    if not user_exists(username):
        click.secho("User '{}' not registered".format(username), fg="red", err=True)
        sys.exit(1)

    permissions = get_permission_info(base_uri)

    if username in permissions["users_with_register_permissions"]:
        click.secho(
            "User '{}' already has register permissions".format(username),
            fg="red",
            err=True,
        )
        sys.exit(1)

    permissions["users_with_register_permissions"].append(username)
    register_permissions(base_uri, permissions)


@user_cli.command(name="token")
@click.argument("username")
@click.option("--last-forever", is_flag=True)
def generate_token(username, last_forever):
    """Generate a token for a user in dserver."""

    if not user_exists(username):
        click.secho("User '{}' not registered".format(username), fg="red", err=True)
        sys.exit(1)

    if last_forever:
        token = create_access_token(identity=username, expires_delta=False)
    else:
        token = create_access_token(identity=username)
    try:
        # Python 2.
        click.secho(token.decode("utf-8"))
    except AttributeError:
        # Python 3
        click.secho(token)


@base_uri_cli.command(name="index")
@click.argument("base_uri")
def index_base_uri(base_uri):
    """Register all the datasets in a base URI."""
    base_uri = dtoolcore.utils.sanitise_uri(base_uri)

    if not base_uri_exists(base_uri):
        click.secho("Base URI '{}' not registered".format(base_uri), fg="red", err=True)
        sys.exit(1)

    for dataset in iter_datasets_in_base_uri(base_uri):
        try:
            dataset_info = generate_dataset_info(dataset, base_uri)
        except Exception as message:
            click.secho(
                "Failed to register: {} {}".format(dataset.name, dataset.uri), fg="red"
            )
            click.echo(message)
            continue

        try:
            r = register_dataset(dataset_info)
        except dservercore.ValidationError as message:
            click.secho(
                "Failed to register: {} {}".format(dataset.name, dataset.uri), fg="red"
            )
            click.echo(message)
            continue

        click.secho("Registered: {}".format(r), fg="green")


@dataset_cli.command(name="register")
@click.argument("uri")
def register(uri):
    """Register specific dataset at URI."""
    uri = dtoolcore.utils.sanitise_uri(uri)

    dataset = DataSet.from_uri(uri)
    base_uri = dataset.base_uri

    if not base_uri_exists(base_uri):
        click.secho("Base URI '{}' not registered".format(base_uri), fg="red", err=True)
        sys.exit(1)

    try:
        dataset_info = generate_dataset_info(dataset, base_uri)
    except Exception as message:
        click.secho(
            "Failed to register: {} {}".format(dataset.name, dataset.uri), fg="red", err=True
        )
        click.echo(message, err=True)
        sys.exit(1)

    try:
        r = register_dataset(dataset_info)
    except dservercore.ValidationError as message:
        click.secho(
            "Failed to register: {} {}".format(dataset.name, dataset.uri), fg="red", err=True
        )
        click.echo(message, err=True)
        sys.exit(1)

    click.secho("Registered: {}".format(r), fg="green")


@config_cli.command(name="show")
def config_show():
    """Print JSON-formatted Flask app config."""
    publishable_config = obj_to_dict(current_app.config, exclusions=CONFIG_EXCLUSIONS)
    click.secho(json.dumps(publishable_config, indent=2))


@config_cli.command(name="versions")
def config_versions():
    """Print JSON-formatted lookup server components and versions."""
    click.secho(json.dumps(versions_to_dict(), indent=2))


app.cli.add_command(user_cli)
app.cli.add_command(base_uri_cli)
app.cli.add_command(dataset_cli)
app.cli.add_command(config_cli)
