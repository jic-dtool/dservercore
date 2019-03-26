"""Command line utility functions."""

from datetime import date, datetime
import json
import sys

import click
import dtoolcore
from dtoolcore.utils import DEFAULT_CONFIG_PATH as CONFIG_PATH
from flask import Flask
from flask_jwt_extended import create_access_token
import yaml

from dtool_lookup_server.utils import (
    base_uri_exists,
    user_exists,
    register_users,
    register_base_uri,
    show_permissions,
    update_permissions,
    register_dataset,
)

app = Flask(__name__)


@app.cli.command()
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


@app.cli.command()
@click.argument('base_uri')
def add_base_uri(base_uri):
    """Register a base URI in the dtool lookup server."""
    if base_uri_exists(base_uri):
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


@app.cli.command()
@click.argument('base_uri')
def index_base_uri(base_uri):
    """Register all the datasets in a base URI."""
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
