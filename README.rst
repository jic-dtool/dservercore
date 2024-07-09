dservercore
===========

.. |dtool| image:: https://github.com/jic-dtool/dservercore/blob/main/icons/22x22/dtool_logo.png?raw=True
    :height: 20px
    :target: https://github.com/jic-dtool/dservercore
.. |pypi| image:: https://img.shields.io/pypi/v/dservercore
    :target: https://pypi.org/project/dservercore/
.. |tag| image:: https://img.shields.io/github/v/tag/jic-dtool/dservercore
    :target: https://github.com/jic-dtool/dservercore/tags
.. |test| image:: https://img.shields.io/github/actions/workflow/status/jic-dtool/dservercore/test.yml?branch=main
    :target: https://github.com/jic-dtool/dservercore/actions/workflows/test.yml
.. |zenodo| image:: https://zenodo.org/badge/123419905.svg
  :target: https://zenodo.org/doi/10.5281/zenodo.12702193

|dtool| |pypi| |tag| |test| |zenodo|

- GitHub: https://github.com/jic-dtool/dservercore
- PyPI: https://pypi.python.org/pypi/dservercore
- Free software: MIT License


Features
--------

- Use a dataset UUID to lookup one more URIs where the dataset is stored
- Search for datasets of interest using free text search
- Built in support to manage users
- Built in support to manage base URIs
- Build in support to manage a user permissions on base URIs
- Built in support for authentication using JSON web tokens


Introduction
------------

`dtool <https://dtool.readthedocs.io>`_ is a command line tool for packaging
data and metadata into a dataset. A dtool dataset manages data and metadata
without the need for a central database.

However, if one has to manage more than a hundred datasets it can be helpful
to have the datasets' metadata stored in a central server to enable one to
quickly find datasets of interest.

``dserver`` provides a web API for registering datasets' metadata
and provides functionality to lookup, list and search for datasets.

When managing many groups data it can be useful to ensure that users can only
access metadata associated with datasets stored in base URI's that they have
been given access to. ``dserver`` therefore provides means to
manage users, base URIs and users' permissions on those base URIs.

``dserver`` is consumed by the `dtool-lookup-client
<https://github.com/jic-dtool/dtool-lookup-client>`_, and the
`dtool-lookup-webapp <https://github.com/jic-dtool/dtool-lookup-webapp>`_.
Third party applications making use of the dserver have also been
created, notably the `livMatS/dtool-lookup-gui
<https://github.com/livMatS/dtool-lookup-gui>`_.

``dservercore`` provides the core Flask app central to dserver's
modular, pluggable framework.

Installation
------------

Install ``dservercore``::

    $ pip install dservercore

For a minimal setup, dserver requires search and retrieve plugins.
Pick search and retrieve plugins of your choice and install those. Here, the
``dserver-search-plugin-mongo`` and ``dserver-retrieve-plugin-mongo``
serve as default for demonstration::

    $ pip install dserver-search-plugin-mongo
    $ pip install dserver-retrieve-plugin-mongo

Setup and configuration
-----------------------

Configure the Flask app
^^^^^^^^^^^^^^^^^^^^^^^

``dserver`` is a Flask app. Flask needs to know where to look for
the app. One therefore needs to define the ``FLASK_APP`` environment variable::

    $ export FLASK_APP=dservercore

Configure search and retrieve plugins
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``dserver`` is agnostic of how descriptive data is stored and
searched. The implementation is delegated to search and retrieve plugins.
Refer to their documentation for details on their configuration.

In the sample case of ``dserver-search-plugin-mongo`` and
``dserver-retrieve-plugin-mongo``, the same Mongo database
can be used for both search and information retrieval.

Create a directory where the MongoDB data will be stored::

    $ mkdir data

Start Mongo DB, for example using docker::

    $ docker run -d -p 27017:27017 -v `pwd`/data:/data/db mongo

Configure the search plugin with::

    export SEARCH_MONGO_URI="mongodb://localhost:27017/"
    export SEARCH_MONGO_DB="dserver"
    export SEARCH_MONGO_COLLECTION="datasets"

and the retrieve plugin with::

    export RETRIEVE_MONGO_URI="mongodb://localhost:27017/"
    export RETRIEVE_MONGO_DB="dserver"
    export RETRIEVE_MONGO_COLLECTION="datasets"

This must happen before issuing any ``flask`` commands as below.

Configure the SQL database
^^^^^^^^^^^^^^^^^^^^^^^^^^

``dserver`` stores administrative metadata in a SQL database.
By default it uses a SQLite database. However, this can be configured by
setting the ``SQLALCHEMY_DATABASE_URI``, i.e using something along the lines of::

    export SQLALCHEMY_DATABASE_URI=mysql://username:password@server/db

Importantly, you will need an according Python connector for whatever SQL database
you decide to use, e.g. `psycopg2` for PostgreSQL or `mysqlclient` for MySQL.

For more information see `flask-SQLAlchemy
<http://flask-sqlalchemy.pocoo.org>`_.

Versioning of the relational database is handled using
`flask-Migrate <https://flask-migrate.readthedocs.io>`_

Populate the SQL database with tables using the commands below::

    $ flask db init
    $ flask db migrate
    $ flask db upgrade

Configure a public and private key pair
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``dserver`` implements authentication using JSON Web Tokens.
Private and public key can for example be generated with::

    openssl genrsa -out /path/to/private/jwt_key 2048
    openssl rsa -in /path/to/private/jwt_key -pubout -outform PEM -out /path/to/public/jwt_key.pub

It is possible to delegate the generation of JSON Web Tokens to a different
service as long as one has access to the public key::

    export JWT_PUBLIC_KEY_FILE=~/.ssh/id_rsa.pub

If one has access to the private key as well one can use the ``flask user
token`` command line utility to generate a token for the user. To enable this
one has to set the ``JWT_PRIVATE_KEY_FILE`` environment variable::

    export JWT_PRIVATE_KEY_FILE=~/.ssh/id_rsa

Mac users be warned that the Mac's implementation ``ssh-keygen`` may result in
files that do not adhere to the RFC standard. As such you may get a warning
along the lines of::

    ValueError: Could not deserialize key data.

In this case you need to find a version of ``ssh-keygen`` that generates files
that adhere to the RFC standard, the easiest is probably to generate them in Linux.

Making use of JSON Web Tokens from a different server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When making use of JSON Web Tokens from a different server it may be easier to
use configure the server using the pubic key directly rather than the public key
file::

    export JWT_PUBLIC_KEY="ssh-rsa XXXXXX user@localhost"

Inspecting the flask app configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Inspect the Flask app configuration with::

    $ flask config show
    {
      "DEBUG": false,
      "TESTING": false,
      "PROPAGATE_EXCEPTIONS": null,
      "SECRET_KEY": "***",
      ...
    }


The output is JSON-formatted with lower-case keys and will include plugin
configuration parameters as well.

Inspect the installed ``dserver`` components with::

    $ flask config versions
    {
      "dservercore": "0.17.2",
      "dserver_retrieve_plugin_mongo": "0.1.0",
      "dserver_search_plugin_mongo": "0.1.0"
    }

Starting the flask app
^^^^^^^^^^^^^^^^^^^^^^

The Flask web app can be started using the command below::

    $ flask run


Populating dserver using the CLI
--------------------------------

Indexing a base URI
^^^^^^^^^^^^^^^^^^^

Datasets can be stored on filesystem and in object storage such as AWS S3.  In
an AWS S3 bucket datasets are stored in a flat structure and the bucket itself
is the base URI. To index all the datasets in the S3 bucket, the base URI, one
first needs to register it in ``dserver``::

    flask base_uri add s3://dtool-demo

One can then index it using the command::

    $ flask base_uri index s3://dtool-demo
    Registered: s3://dtool-demo/8ecd8e05-558a-48e2-b563-0c9ea273e71e
    Registered: s3://dtool-demo/907e1b52-d649-476a-b0bc-643ef769a7d9
    Registered: s3://dtool-demo/af6727bf-29c7-43dd-b42f-a5d7ede28337
    Registered: s3://dtool-demo/ba92a5fa-d3b4-4f10-bcb9-947f62e652db
    Registered: s3://dtool-demo/c58038a4-3a54-425e-9087-144d0733387f
    Registered: s3://dtool-demo/faa44606-cb86-4877-b9ea-643a3777e021

It is possible to list all the base URIs registered in ``dserver``::

    $ flask base_uri list
    [
      {
        "base_uri": "s3://dtool-demo",
        "users_with_search_permissions": [],
        "users_with_register_permissions": []
      }
    ]

In the output above it is worth noting that there are two types of permissions
associated with a base URI. "Search" permissions allow a user to search for
datasets in a base URI. "Register" permissions allow a user to register a
dataset in ``dserver`` if it is stored in the specific base URI.


Adding a user and managing permissions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The command below adds the user ``olssont`` to ``dserver``::

    $ flask user add olssont

The command below gives the user ``olssont`` search permissions on the
``s3://dtool-demo`` base URI::

    $ flask user search_permission olssont s3://dtool-demo

The command below gives the user ``olssont`` register permissions on the
``s3://dtool-demo`` base URI::

    $ flask user register_permission olssont s3://dtool-demo


Creating an admin user
^^^^^^^^^^^^^^^^^^^^^^

The command below adds the user ``overlord``, with admin privileges, to the
dtool lookup server::

    $ flask user add --is_admin overlord


Generating a JSON Web Token for a registered user
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The command below can be used to generate a token for a user to authenticate
with when using the web API::

    $ flask user token olssont
    eyJhbGciOiJSUzI1NiIsInR5... (truncated)


Listing the registered users
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The command below lists the users registered in ``dserver``::

    $ flask user list
    [
      {
        "username": "olssont",
        "is_admin": false,
        "register_permissions_on_base_uris": [
          "s3://dtool-demo"
        ],
        "search_permissions_on_base_uris": [
          "s3://dtool-demo"
        ]
      },
      {
        "username": "overlord",
        "is_admin": true,
        "register_permissions_on_base_uris": [],
        "search_permissions_on_base_uris": []
      }
    ]


Deleting a user
^^^^^^^^^^^^^^^

The command below can be used to delete a user::

    $ flask user delete overlord


Adding and removing admin privileges from an existing user
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The command below can be used to give an existing user admin privileges::

    $ flask user update --is_admin olssont

The command below can be used to remove admin privileges from an existing user::

    $ flask user update olssont


dserver API
-----------

``dserver`` makes use of the authorized header to pass through the
JSON web token for authorization. Below we create environment variables for the
token and the header used in the ``curl`` commands::

    $ TOKEN=$(flask user token olssont)
    $ HEADER="Authorization: Bearer $TOKEN"


Standard user usage
^^^^^^^^^^^^^^^^^^^

Looking up URIs based on a dataset's UUID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dataset can be uniquely identified by it's UUID (Universally Unique
Identifier). Below we create an environment variable with the UUID of a dataset
in the s3://dtool-demo bucket::

    $ UUID=8ecd8e05-558a-48e2-b563-0c9ea273e71e

It is possible to list all the location a dataset is located in using the
command below::

    $ curl -H $HEADER http://localhost:5000/uuids/$UUID

Response content::

    [
      {
        "base_uri": "s3://dtool-demo",
        "name": "Escherichia-coli-ref-genome",
        "uri": "s3://dtool-demo/8ecd8e05-558a-48e2-b563-0c9ea273e71e",
        "uuid": "8ecd8e05-558a-48e2-b563-0c9ea273e71e"
      }
    ]

Note that it is possible for a dataset to be registered in more than one base
URI. As such looking up a dataset by UUID can result in multiple hits.


Summary information about datasets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An overall summary of datasets accessible to a user can be accessed using the request below::

    $ curl -H "$HEADER" http://localhost:5000/users/olssont/summary

The response will contain JSON content along the lines of::

    {
        "number_of_datasets": 3,
        "creator_usernames": ["queen"],
        "base_uris": ["s3://mr-men", "s3://snow-white"],
        "datasets_per_creator": {"queen": 3},
        "datasets_per_base_uri": {"s3://mr-men": 1, "s3://snow-white": 2},
        "tags": ["fruit", "veg"],
        "datasets_per_tag": {"fruit": 2, "veg": 1}
    }


Listing all datasets
~~~~~~~~~~~~~~~~~~~~

All the dataset's that a user has permissions to search for can be listed using
the request below::

    $ curl -H "$HEADER" http://localhost:5000/uris

Some of the output of the command above is displayed below::

    [
      {
        "base_uri": "s3://dtool-demo",
        "created_at": 1604860720.736269,
        "creator_username": "olssont",
        "frozen_at": 1604864525.691079,
        "name": "Escherichia-coli-ref-genome",
        "uri": "s3://dtool-demo/8ecd8e05-558a-48e2-b563-0c9ea273e71e",
        "uuid": "8ecd8e05-558a-48e2-b563-0c9ea273e71e"
      },
      ... (truncated)
      {
        "base_uri": "s3://dtool-demo",
        "created_at": 1604860720.736269,
        "creator_username": "olssont",
        "frozen_at": 1604864525.691079,
        "name": "Escherichia-coli-reads-ERR022075",
        "uri": "s3://dtool-demo/faa44606-cb86-4877-b9ea-643a3777e021",
        "uuid": "faa44606-cb86-4877-b9ea-643a3777e021"
      }
    ]



Searching for specific datasets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The command below does a full text search for the word "microscopy" in the descriptive metadata::

    $ curl -H "$HEADER" -H "Content-Type: application/json"  \
        -X POST -d '{"free_text": "microscopy"}'  \
        http://localhost:5000/uris

Below is the result of this search::

    [
      {
        "base_uri": "s3://dtool-demo",
        "created_at": "1530803916.74",
        "creator_username": "olssont",
        "frozen_at": "1536749825.85",
        "name": "hypocotyl3",
        "uri": "s3://dtool-demo/ba92a5fa-d3b4-4f10-bcb9-947f62e652db",
        "uuid": "ba92a5fa-d3b4-4f10-bcb9-947f62e652db"
      }
    ]

Below is a JSON string specifying a more complex query that will search for
datasets with "apples" in the "s3://snow-white" bucket created by either
"grumpy" or "dopey", and has both of the tags "fruit" and "veg"::

    {
        "base_uris": ["s3://snow-white"],
        "creator_usernames": ["grumpy", "dopey"],
        "free_text": "apples",
        "tags": ["fruit", "veg"]
    }

.. note:: The search engine make use of "OR" logic for the items in
          ``base_uris`` and ``creator_usernames`` lists, but uses
          "AND" logic for filtering the search based on the items
          in the ``tags`` list.


Accessing a dataset's readme, annotations and manifest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The command below retrieves the readme for the dataset with the
URI ``s3://dtool-demo/ba92a5fa-d3b4-4f10-bcb9-947f62e652db``::

    $ curl -H "$HEADER" -H "Content-Type: application/json"  \
        http://localhost:5000/readmes/s3/dtool-demo/ba92a5fa-d3b4-4f10-bcb9-947f62e652db

The command below retrieves the annotations for the dataset with the
URI ``s3://dtool-demo/ba92a5fa-d3b4-4f10-bcb9-947f62e652db``::

    $ curl -H "$HEADER" -H "Content-Type: application/json"  \
        http://localhost:5000/annotations/s3/dtool-demo/ba92a5fa-d3b4-4f10-bcb9-947f62e652db

The command below retrieves the tags for the dataset with the
URI ``s3://dtool-demo/ba92a5fa-d3b4-4f10-bcb9-947f62e652db``::

    $ curl -H "$HEADER" -H "Content-Type: application/json"  \
        http://localhost:5000/tags/s3/dtool-demo/ba92a5fa-d3b4-4f10-bcb9-947f62e652db

The command below retrieves the manifest for the dataset with the
URI ``s3://dtool-demo/ba92a5fa-d3b4-4f10-bcb9-947f62e652db``::

    $ curl -H "$HEADER" -H "Content-Type: application/json"  \
        http://localhost:5000/manifests/s3/dtool-demo/ba92a5fa-d3b4-4f10-bcb9-947f62e652db


Getting information about one's own permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A user can find out about his/her own permissions using the command below::

    $ curl -H "$HEADER" http://localhost:5000/users/olssont

Response content::

    {
      "is_admin": false,
      "register_permissions_on_base_uris": [
        "s3://dtool-demo"
      ],
      "search_permissions_on_base_uris": [
        "s3://dtool-demo"
      ],
      "username": "olssont"
    }

Data champion user usage
^^^^^^^^^^^^^^^^^^^^^^^^

A data champion is different from a regular user in that he/she has
"register" permissions on a base URI. This means that a data champion
can register metadata about a data to ``dserver``.

Registering a dataset
~~~~~~~~~~~~~~~~~~~~~

Below is an example of how to register a dataset::

    $ DATASET_INFO='
    {
      "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "base_uri": "s3://dtool-demo",
      "uri": "s3://dtool-demo/8ecd8e05-558a-48e2-b563-0c9ea273e71e",
      "name": "Escherichia-coli-ref-genome",
      "type": "dataset",
      "readme": "{\"accession_id\":\"U00096.3\",\"description\":\"U00096.3genomewithBowtie2indices\",\"index_build_cmd\":\"bowtie2-buildU00096.3.fastareference\",\"index_builder\":\"bowtie2-buildversion2.3.3\",\"link\":\"https://www.ebi.ac.uk/ena/data/view/U00096.3\",\"organism\":\"Escherichiacolistr.K-12substr.MG1655\"},",
      "manifest": {
        "dtoolcore_version": "3.18.2",
        "hash_function": "md5sum_hexdigest",
        "items": {
          "26f0d76fb3c3e34f0c7c8b7c3461b7495761835c": {
            "hash": "06d80eb0c50b49a509b49f2424e8c805",
            "relpath": "dog.txt",
            "size_in_bytes": 3,
            "utc_timestamp": 1716979579.898408
          },
          "d25102a700e072b528db79a0f22b3a5ffe5e8f5d": {
            "hash": "68238cd792d215bdfdddc7bbb6d10db4",
            "relpath": "parrot.txt",
            "size_in_bytes": 6,
            "utc_timestamp": 1716979579.902415
          }
        }
      },
      "creator_username": "olssont",
      "frozen_at": "1537916653.7",
      "created_at": "1537802877.62",
      "annotations": {},
      "tags": [],
      "number_of_items": 2,
      "size_in_bytes": 9
    }'
    $ curl -H "$HEADER" -H "Content-Type: application/json"  \
        -X PUT -d "$DATASET_INFO"  \
        http://localhost:5000/uris/s3/dtool-demo/ba92a5fa-d3b4-4f10-bcb9-947f62e652db

The required keys are defined in the variable
``dservercore.utils.DATASET_INFO_REQUIRED_KEYS``.

Admin user usage
^^^^^^^^^^^^^^^^

The administrative user can register new users, base URIs and manage who has
permissions to search for and register datasets. Below we update the header
to use the token from the ``overlord`` admin user::

    $ TOKEN=$(flask user token overlord)
    $ HEADER="Authorization: Bearer $TOKEN"


Listing registered users
~~~~~~~~~~~~~~~~~~~~~~~~

To list all the registered users an admin user can use the below::

    $ curl -H "$HEADER" http://localhost:5000/users

Response content::

    [
      {
        "is_admin": false,
        "username": "olssont"
      },
      {
        "is_admin": true,
        "username": "overlord"
      }
    ]


Registering users
~~~~~~~~~~~~~~~~~

An admin user can register other users::

    $ curl -H "$HEADER" -H "Content-Type: application/json"  \
        -X PUT -d '{"username": "joe", "is_admin": true}'  \
        http://localhost:5000/users/joe




Registering a base URI
~~~~~~~~~~~~~~~~~~~~~~

An admin user can register a new base URI ``s3://another-bucket``::

    $ curl -H "$HEADER" -H "Content-Type: application/json"  \
        -X PUT -d '{
          "base_uri": "s3://another-bucket",
          "users_with_search_permissions": ["joe"],
          "users_with_register_permissions": ["olssont"]
        }' http://localhost:5000/base-uris/s3/another-bucket


Listing registered base URIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An admin user can list all registered base URIs::

    $ curl -H "$HEADER" http://localhost:5000/base-uris

Response content::

    [
      {
        "base_uri": "s3://dtool-demo",
      },
      {
        "base_uri": "s3://another-bucket",
      }
    ]


Updating the permissions on a base URI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An admin user can update the permissions on a base URI
simply by another `PUT` request::

    $ curl -H "$HEADER" -H "Content-Type: application/json"  \
        -X PUT -d '{
          "base_uri": "s3://another-bucket",
          "users_with_search_permissions": ["joe", "olssont"],
          "users_with_register_permissions": ["olssont"]
        }' http://localhost:5000/base-uris/s3/another-bucket

Note that the request below can be used to clear all existing permissions::

    $ curl -H "$HEADER" -H "Content-Type: application/json"  \
        -X PUT -d '{
          "base_uri": "s3://another-bucket",
          "users_with_register_permissions": [],
          "users_with_search_permissions": []}'  \
        http://localhost:5000/base-uris/s3/another-bucket


Getting information about the permissions on a base URI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An admin user can get information about the permissions on a base URI::

    $ curl -H "$HEADER" -H "Content-Type: application/json"  \
        http://localhost:5000/base-uris/s3/another-bucket

Response content::

    {
      "base_uri": "s3://another-bucket",
      "users_with_register_permissions": [],
      "users_with_search_permissions": []
    }

Querying server configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The request::

    $ curl -H "$HEADER" http://localhost:5000/config/info

will return the current server configuration with all keys in lowercase, i.e.::

    {
      "config": {
        "allow_access_from": "0.0.0.0/0",
        "allow_direct_aggregation": true,
        "allow_direct_query": true,
        ...
      }
    }

The request::

    $ curl http://localhost:5000/config/versions

will return all components, i.e. server core, search, retrieve
and extension plugins with their versions, i.e.::

    {
      "versions": {
        "dservercore": "0.17.2",
        "dserver_retrieve_plugin_mongo": "0.1.0",
        "dserver_search_plugin_mongo": "0.1.0"
      }
    }

This request does not require any authorization.

Creating a plugin
-----------------

It is possible to create add plugins to this system. This is achieved by
creating a separate Python package containing a `Flask blueprint
<https://flask.palletsprojects.com/en/1.1.x/blueprints/>`_.

A basic plugin could consist of a single ``__init__`` and a ``setup.py``
or ``pyproject.toml`` file in the directory structure below::

    .
    |-- my_plugin
    |   `-- __init__.py
    `-- setup.py


The ``__init__.py`` file could contain the code below. Importantly, the
plugin has to implement a derivative of ``dtoolcore.ExtensionABC``.

.. code-block:: python

    from flask_smorest import Blueprint
    from dtoolcore import ExtensionABC

    my_plugin_bp = Blueprint('my_plugin', __name__, url_prefix="/my_plugin")

    @my_plugin_bp.route('/', methods=["GET"])
    @my_plugin_bp.response(200)
    def show(page):
        return "My plugin content"

    class NotificationExtension(ExtensionABC):

        def register_dataset(self, dataset_info):
            """Register or update a dataset entry by replacing a possibly existing entry."""
            pass

        def get_blueprint(self):
            """Return the Flask blueprint to be used for the extension."""
            return my_plugin_bp

Classes adhering to the interface of the ``dservercore.ExtensionABC`` abstract base class
need to be associated with the ``dservercore.extension`` entrypoint in the Python package
``setup.py`` file or ``pyproject.toml``. The ``setup.py`` file would need to look something along the
lines of the below.

.. code-block:: python

    from setuptools import setup

    setup(
        name="my-plugin",
        packages=["my_plugin"],
        install_requires=[
            "dservercore",
        ],
        entry_points={
            "dservercore.extension": [
                "my_plugin=my_plugin:my_plugin_bp",
            ],
        }
    )

A respective entry in a ``pyproject.toml`` would look as follows.

.. code-block:: toml

    [project.entry-points."dservercore.extension"]
    "MyExtension" = "dserver_extension_module:MyExtension"

Examples of actual plugins include:

- `dserver-direct-mongo-plugin <https://github.com/livMatS/dserver-direct-mongo-plugin>`_
- `dserver-dependency-graph-plugin <https://github.com/livMatS/dserver-dependency-graph-plugin>`_
- `dserver-notification-plugin <https://github.com/livMatS/dserver-notification-plugin>`_
