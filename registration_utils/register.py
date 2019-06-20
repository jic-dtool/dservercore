import click
import requests
import yaml

with open("projects.yml") as fh:
    PROJECTS = yaml.load(fh, Loader=yaml.FullLoader)


def get_header(token):
    """Return HTTP header."""
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }



@click.group()
def register():
    "Register base URIs, users, permissions and data in dtool-lookup-server."


@register.command()
@click.argument("token")
@click.argument("lookup_server_url")
def base_uris(token, lookup_server_url):
    "Register base URIs."
    for b_uri in PROJECTS.keys():
        data = {"base_uri": b_uri}
        response = requests.post(
            lookup_server_url + "/admin/base_uri/register",
            headers=get_header(token),
            json=data
        )
        print(data)
        print(response.status_code, response.reason)


@register.command()
@click.argument("token")
@click.argument("lookup_server_url")
def users(token, lookup_server_url):
    "Register users."
    users = set()
    for base_uri, permissions in PROJECTS.items():
        for p in ["register", "search"]:
            for u in permissions[p]:
                users.add(u)
    data = []
    for u in users:
        data.append({"username": u})

    response = requests.post(
        lookup_server_url + "/admin/user/register",
        headers=get_header(token),
        json=data
    )
    print(data)
    print(response.status_code, response.reason)


@register.command()
@click.argument("token")
@click.argument("lookup_server_url")
def permissions(token, lookup_server_url):
    "Register permissions."
    for b_uri, permissions in PROJECTS.items():
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
            json=data
        )
        print(data)
        print(response.status_code, response.reason)


if __name__ == "__main__":
    register()
