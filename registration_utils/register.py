import click
import requests
import yaml

from dtoolcore import iter_datasets_in_base_uri

from dserver.utils import generate_dataset_info


def get_projects(fpath):
    """Return projects dictionary."""
    with open(fpath) as fh:
        projects = yaml.load(fh, Loader=yaml.FullLoader)
    return projects


def get_header(token):
    """Return HTTP header."""
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }


def register_base_uris(projects_fpath, token, lookup_server_url):
    "Register base URIs."
    projects = get_projects(projects_fpath)
    for b_uri in projects.keys():
        data = {"base_uri": b_uri}
        response = requests.post(
            lookup_server_url + "/admin/base_uri/register",
            headers=get_header(token),
            json=data,
            verify=False
        )
        print(data)
        print(response.status_code, response.reason)


def register_users(projects_fpath, token, lookup_server_url):
    "Register users."
    projects = get_projects(projects_fpath)
    users = set()
    for base_uri, permissions in projects.items():
        for p in ["register", "search"]:
            for u in permissions[p]:
                users.add(u)
    data = []
    for u in users:
        data.append({"username": u})

    response = requests.post(
        lookup_server_url + "/admin/user/register",
        headers=get_header(token),
        json=data,
        verify=False
    )
    print(data)
    print(response.status_code, response.reason)


def register_permissions(projects_fpath, token, lookup_server_url):
    "Register permissions."
    projects = get_projects(projects_fpath)
    for b_uri, permissions in projects.items():
        data = {"base_uri": b_uri}

        register_permissions = []
        for u in permissions["register"]:
            register_permissions.append(u)
        data["users_with_register_permissions"] = register_permissions

        search_permissions = []
        for u in permissions["search"]:
            search_permissions.append(u)
        data["users_with_search_permissions"] = search_permissions

        response = requests.post(
            lookup_server_url + "/admin/permission/update_on_base_uri",
            headers=get_header(token),
            json=data,
            verify=False
        )
        print(data)
        print(response.status_code, response.reason)


def register_data(projects_fpath, token, lookup_server_url):
    "Register data."
    projects = get_projects(projects_fpath)
    for b_uri in projects.keys():
        for dataset in iter_datasets_in_base_uri(b_uri):
            print(dataset.uri)
            try:
                dataset_info = generate_dataset_info(dataset, b_uri)
            except:  # NOQA
                print("Failed to generate dataset info")
                continue
            response = requests.post(
                lookup_server_url + "/dataset/register",
                headers=get_header(token),
                json=dataset_info,
                verify=False
            )
            print(response.status_code, response.reason)


@click.group()
def register():
    "Register base URIs, users, permissions and data in dserver."


@register.command()
@click.argument("projects_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("token")
@click.argument("lookup_server_url")
def base_uris(projects_file, token, lookup_server_url):
    "Register base URIs."
    register_base_uris(projects_file, token, lookup_server_url)


@register.command()
@click.argument("projects_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("token")
@click.argument("lookup_server_url")
def users(projects_file, token, lookup_server_url):
    "Register users."
    register_users(projects_file, token, lookup_server_url)


@register.command()
@click.argument("projects_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("token")
@click.argument("lookup_server_url")
def permissions(projects_file, token, lookup_server_url):
    "Register permissions."
    register_permissions(projects_file, token, lookup_server_url)


@register.command()
@click.argument("projects_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("token")
@click.argument("lookup_server_url")
def data(projects_file, token, lookup_server_url):
    "Register data."
    register_data(projects_file, token, lookup_server_url)


@register.command()
@click.argument("projects_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("token")
@click.argument("lookup_server_url")
def all(projects_file, token, lookup_server_url):
    "Register base URI, users, permissions and data."
    register_base_uris(projects_file, token, lookup_server_url)
    register_users(projects_file, token, lookup_server_url)
    register_permissions(projects_file, token, lookup_server_url)
    register_data(projects_file, token, lookup_server_url)


if __name__ == "__main__":
    register()
