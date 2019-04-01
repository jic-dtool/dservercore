"""Command line utility functions."""

from datetime import date, datetime
import json
import sys

import click
import dtoolcore
import dtoolcore.utils
from dtoolcore.utils import DEFAULT_CONFIG_PATH as CONFIG_PATH
from flask import Flask
from flask.cli import AppGroup
from flask_jwt_extended import create_access_token
import yaml

import dtool_lookup_server.utils
from dtool_lookup_server.utils import (
    base_uri_exists,
    user_exists,
    register_users,
    register_base_uri,
    get_permission_info,
    update_permissions,
    register_dataset,
)

app = Flask(__name__)

user_cli = AppGroup('user', help="User management commands.")
base_uri_cli = AppGroup('base_uri', help="Base URI management commands.")


@user_cli.command(name="add")
@click.argument('username')
@click.option('-a', '--is_admin', is_flag=True)
def register_user(username, is_admin):
    """Register a user in the dtool lookup server."""

    if user_exists(username):
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


@user_cli.command(name="list")
def list_users():
    """List the users in the dtool lookup server."""
    click.secho(
        json.dumps(dtool_lookup_server.utils.list_users(), indent=2)
    )


@base_uri_cli.command(name="add")
@click.argument('base_uri')
def add_base_uri(base_uri):
    """Register a base URI in the dtool lookup server."""
    base_uri = dtoolcore.utils.sanitise_uri(base_uri)
    if base_uri_exists(base_uri):
        click.secho(
            "Base URI '{}' already registered".format(base_uri),
            fg="red",
            err=True
        )
        sys.exit(1)

    register_base_uri(base_uri)


@base_uri_cli.command(name="list")
def list_base_uris():
    """List the base URIs in the dtool lookup server."""
    click.secho(
        json.dumps(dtool_lookup_server.utils.list_base_uris(), indent=2)
    )


@user_cli.command(name="search_permission")
@click.argument('username')
@click.argument('base_uri')
def give_search_permission(username, base_uri):
    """Give a user search permission on a base URI."""

    if not base_uri_exists(base_uri):
        click.secho(
            "Base URI '{}' not registered".format(base_uri),
            fg="red",
            err=True
        )
        sys.exit(1)

    if not user_exists(username):
        click.secho(
            "User '{}' not registered".format(username),
            fg="red",
            err=True
        )
        sys.exit(1)

    permissions = get_permission_info(base_uri)

    if username in permissions["users_with_search_permissions"]:
        click.secho(
            "User '{}' already has search permissions".format(username),
            fg="red",
            err=True
        )
        sys.exit(1)

    permissions["users_with_search_permissions"].append(username)
    update_permissions(permissions)


@user_cli.command(name="register_permission")
@click.argument('username')
@click.argument('base_uri')
def give_register_permission(username, base_uri):
    """Give a user register permission on a base URI."""

    if not base_uri_exists(base_uri):
        click.secho(
            "Base URI '{}' not registered".format(base_uri),
            fg="red",
            err=True
        )
        sys.exit(1)

    if not user_exists(username):
        click.secho(
            "User '{}' not registered".format(username),
            fg="red",
            err=True
        )
        sys.exit(1)

    permissions = get_permission_info(base_uri)

    if username in permissions["users_with_register_permissions"]:
        click.secho(
            "User '{}' already has register permissions".format(username),
            fg="red",
            err=True
        )
        sys.exit(1)

    permissions["users_with_register_permissions"].append(username)
    update_permissions(permissions)


@user_cli.command(name="token")
@click.argument('username')
@click.option("--last-forever", is_flag=True)
def generate_token(username, last_forever):
    """Generate a token for a user in the dtool lookup server."""

    if not user_exists(username):
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


def _json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type {} not serializable".format(type(obj)))


@base_uri_cli.command(name="index")
@click.argument('base_uri')
def index_base_uri(base_uri):
    """Register all the datasets in a base URI."""
    base_uri = dtoolcore.utils.sanitise_uri(base_uri)

    if not base_uri_exists(base_uri):
        click.secho(
            "Base URI '{}' not registered".format(base_uri),
            fg="red",
            err=True
        )
        sys.exit(1)

    base_uri = dtoolcore.utils.sanitise_uri(base_uri)
    StorageBroker = dtoolcore._get_storage_broker(base_uri, CONFIG_PATH)
    for uri in StorageBroker.list_dataset_uris(base_uri, CONFIG_PATH):
        try:
            dataset = dtoolcore.DataSet.from_uri(uri)
        except dtoolcore.DtoolCoreTypeError:
            pass
        dataset_info = dataset._admin_metadata
        dataset_info["uri"] = dataset.uri
        dataset_info["base_uri"] = base_uri

        # Add the readme info.
        readme_info = yaml.load(dataset.get_readme_content())
        dataset_info["readme"] = readme_info

        # Clean up datetime.data.
        dataset_info_json_str = json.dumps(dataset_info, default=_json_serial)
        dataset_info = json.loads(dataset_info_json_str)

        r = register_dataset(dataset_info)
        click.secho("Registered: {}".format(r))


app.cli.add_command(user_cli)
app.cli.add_command(base_uri_cli)
