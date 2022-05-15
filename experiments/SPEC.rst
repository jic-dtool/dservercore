Architectural restructuring specification
=========================================

User stories
------------

As a systems administrator tasked with installing and evaluating the
dtool-lookup-server I want to be able to install a minimal working system using
as few commands, databases and environment variables as possible so that I can
get a proof of concept up and running as quickly as possible.

As a DevOps engineer tasked with installing and maintaining a
dtool-lookup-server I want to be able to configure it to run in a way that is
consistent with my other production systems to keep my tool chain as lean and
consistent as possible. The dtool-lookup-server should therefore not have
strong opinions on things like systemd, docker-compose, kubernetes. Rather it
should be able to fit into any of these systems.

As a software engineer tasked with making a cloud native implementation of the
dtool-lookup-server I want to be able to swap out any components that rely on
databases so that I can make my own plug-ins that use cloud databases to
replace these components.

As a software engineer tasked with extending the dtool-lookup-server with new
functionality I want to be able to develop my own Python package that plugs
into the system without having to touch any of the code used to run the base
installation of the dtool-lookup-server, and I want to have access to abstract
base classes to inherit from to help guide my development efforts.

As a consumer of the dtool-lookup-server REST API I want to be able to create
clients that auto-discover the API to make it easier to maintain the clients
when the dtool-lookup-server REST API is updated.


Minimal install for evaluation
------------------------------

::

    pip install dtool-lookup-server-core
    pip install dtool-lookup-server-search-pg
    pip install dtool-lookup-server-auth-jwt

    export FLASK_APP=dtool_lookup_server

    # The exports below will depend on which search packages is installed.
    export DLS_PG_URI=<postgres URI>
    export DLS_PG_USER=<postgres user name>
    export DLS_PG_PASSWORD=<postgres password>

    # The exports below will depend on the auth package installed.
    export DLS_JWT_PRIVATE_KEY_FILE=~/.ssh/id_rsa
    export DLS_JWT_PUBLIC_KEY_FILE=~/.ssh/id_rsa.pub

    flask db init
    flask db migrate
    flask db upgrade

    flask run


Swapping out the search module
------------------------------


Create a Python package called something like `my_dtool_lookup_search` with
code along the lines of the below exposed in the `__init__.py` file.


.. code-block:: python

    from dtool_lookup_server_core import SearchABC

    class MySearch(SearchABC):

        def register_dataset(dataset_info):
            """Logic to register the dataset in the custom DB used."""

        def search(query):
            """Logic to convert the query into the custom DB language."""

        def lookup_uris(uuid):

            """Logic to return a list of dataset URIs from a uuid."""

Expose the custom class to the core system by exposing it as an entry point in
the `setup.py` file.

.. code-block:: python

    from setuptools import setup
    setup(
        name="my_dtool_lookup_search",
        packages=["my_dtool_lookup_search"],
        install_requires=["dtool_lookup_server_core"],
        entry_points={
            "dtool_lookup_server.search": [
                "klass=my_dtool_lookup_search:MySearch",
            ],
        },
    )


Swapping out the auth module
----------------------------


Create a Python package called something like `my_dtool_lookup_auth` with
code along the lines of the below exposed in the `__init__.py` file.


.. code-block:: python

    from dtool_lookup_server_core import AuthABC

    class MyAuth(AuthABC):

        def has_admin_rights(username):
            pass

        def give_admin_rights(username):
            pass

        def remove_admin_rights(username):
            pass

        def get_user_info(username):
            pass

        def may_search(username, base_uri):
            pass

        def may_register(username, base_uri):
            pass

        def register_base_uri(base_uri):
            pass

        def register_user(user_info):
            pass

        def get_base_uris(username):
            pass

        def grant_user_search(username, base_uri):
            pass

        def grant_user_register(username, base_uri):
            pass

        def revoke_user_search(username, base_uri):
            pass

        def revoke_user_register(username, base_uri):
            pass

        def update_all_permissions(base_uri, users_with_search_permissisons, users_with_register_permissions):
            pass

        def get_permissions(base_uri):
            pass

        def list_users():
            pass


Expose the custom class to the core system by exposing it as an entry point in
the `setup.py` file.

.. code-block:: python

    from setuptools import setup
    setup(
        name="my_dtool_lookup_auth",
        packages=["my_dtool_lookup_auth"],
        install_requires=["dtool_lookup_server_core"],
        entry_points={
            "dtool_lookup_server.auth": [
                "klass=my_dtool_lookup_auth:MyAuth",
            ],
        },
    )


Creating a custom extension
---------------------------


Create a Python package called something like `my_dtool_lookup_extension` with
code along the lines of the below exposed in the `__init__.py` file.


.. code-block:: python

    from dtool_lookup_server_core import ExtensionABC

    # Use the helper functions below to implement relevant access policies.
    from dtool_lookup_server_core.utils import (
        has_admin_rights,
        may_search,
        may_register,
        list_search_base_uris,
    )

    class MyExtension(ExtensionABC):

        def register_dataset(dataset_info):
            """Logic to register the dataset in the custom DB used."""

        def register_base_uri(base_uri):
            """Logic to register a base URI in the custom DB used."""
            pass

        def core.ExtensionABC.get_blueprint():
            """Return the Flask blueprint with URL endpoints to expose."""


Expose the custom class to the core system by exposing it as an entry point in
the `setup.py` file.

.. code-block:: python

    from setuptools import setup
    setup(
        name="my_dtool_lookup_extension",
        packages=["my_dtool_lookup_extension"],
        install_requires=["dtool_lookup_server_core"],
        entry_points={
            "dtool_lookup_server.extentsion": [
                "klass=my_dtool_lookup_extension:MyExtension",
            ],
        },
    )


Components
----------

Core
^^^^

The core includes three abstract base classes that are implemented by other
components.

- `core.AuthABC`
- `core.SearchABC`
- `core.ExtenstionABC`

The core module implements the bluprints.

- `admin`
- `config`
- `dataset`
- `user`

The blueprints above expose the routes.

- `/admin/base_uri/register` (implemented in `Search.register_base_uri` and
  `Extenstion.register_base_uri`)
- `/admin/base_uri/list` (implemented in `Search.get_base_uris`)
- `/admin/permissions/info` (implemented in `Auth.get_permissions`)
- `/admin/permissions/update_on_base_uri` (implemented in `Auth.update_all_permissions`)
- `/admin/permissions/grant_user_search` (implemented in `Auth.grant_user_search`)
- `/admin/permissions/grant_user_register` (implemented in `Auth.grant_user_register`)
- `/admin/permissions/revoke_user_search` (implemented in `Auth.revoke_user_search`)
- `/admin/permissions/revoke_user_register` (implemented in `Auth.revoke_user_register`)
- `/admin/user/register` (implemented in `Auth.register_user`)
- `/admin/user/list` (implemented in `Auth.list_users`)
- `/admin/user/give_admin_rights` (implemented in `Auth.give_admin_rights`)
- `/admin/user/remove_admin_rights` (implemented in `Auth.remove_admin_rights`)
- `/config/info` (implemented in `Core.get_info`)
- `/dataset/summary` (implemented in `Search.get_summary`)
- `/dataset/lookup/<uuid>` (implemented in `Search.lookup_uuid`)
- `/dataset/search` (implemented in `Search.search`)
- `/dataset/register` (implemented in `Search.register_dataset` and
  `Extenstion.register_dataset`)
- `/dataset/manifest` (implemented in `Search.get_manifest`)
- `/dataset/readme` (implemented in `Search.get_readme`)
- `/dataset/annotations` (implemented in `Search.get_annotations`)
- `/user/info/<username>` (implemented in `Auth.get_user_info`)


The component package also exposes a number of utility functions that can be
imported by other modules.

- `core.utils.has_admin_rights(username)`
- `core.utils.may_search(username, base_uri)`
- `core.utils.may_register(username, base_uri)`
- `core.utils.list_search_base_uris(username)`



Auth
^^^^

The auth component is all about base URIs, users and the permissions that grant
users the ability to register datasets and search for datasets in base URIs.

It also has the concept of giving and removing admin rights from users.

An auth component needs to implement a concrete implementation of the
abstract base class `core.AuthABC`.

Below are the methods that need to be implemented when actualising the
`core.AuthABC` abstract base class.

- `core.AuthABC.has_admin_rights(username)`
- `core.AuthABC.give_admin_rights(username)`
- `core.AuthABC.remove_admin_rights(username)`
- `core.AuthABC.get_user_info(username)`
- `core.AuthABC.may_search(username, base_uri)`
- `core.AuthABC.may_register(username, base_uri)`
- `core.AuthABC.register_base_uri(base_uri)`
- `core.AuthABC.register_user(user_info)`
- `core.AuthABC.get_base_uris(username)`
- `core.AuthABC.grant_user_search(username, base_uri)`
- `core.AuthABC.grant_user_register(username, base_uri)`
- `core.AuthABC.revoke_user_search(username, base_uri)`
- `core.AuthABC.revoke_user_register(username, base_uri)`
- `core.AuthABC.update_all_permissions(base_uri, users_with_search_permissisons, users_with_register_permissions)`
- `core.AuthABC.get_permissions(base_uri)`
- `core.AuthABC.list_users()`


Search
^^^^^^

The search component is all about searching for datasets based upon the
metadata used to describe the datasets.

A search component needs to implement a concreate implementation of the
abstract base class `core.SearchABC`.

Below are the methods that need to be implemented when actualising the
`core.SearchABC` abstract base class.

- `core.SearchABC.register_dataset(dataset_info)`
- `core.SearchABC.search(query)`
- `core.SearchABC.lookup_uris(uuid)`


Metadata
^^^^^^^^

The metadata component is all about retrieving pieces of metadata relating to a
dataset.

A metadata component needs to implement a concrete implementation of the
abstract base class `core.MetadataABC`.

Below are the methods that need to be implemented when actualising the
`core.MetadataABC` abstract base class.

- `core.SearchABC.register_dataset(dataset_info)`
- `core.MetadataABC.get_manifest(dataset_uri)`
- `core.MetadataABC.get_readme(dataset_uri)`
- `core.MetadataABC.get_annotations(dataset_uri)`


TODO: work out what to do with this outlier

- `core.MetadataABC.get_summary(username)`


ExtensionABC
^^^^^^^^^^^^

A extension component needs to implement a concreate implementation of the
abstract base class `core.ExtensionABC`.

Below are the methods that need to be implemented when actualising the
`core.ExtenstionABC` abstract base class.

- `core.ExtensionABC.register_dataset(dataset_info)`
- `core.ExtensionABC.register_base_uri(base_uri)`
- `core.ExtensionABC.get_blueprint()`


Further reading
---------------

- `The Tweleve-Factor App <https://12factor.net/>`_
