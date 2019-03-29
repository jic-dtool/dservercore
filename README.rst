Dtool Lookup Server
===================

Dtool Lookup Server is an application that given a dataset UUID returns a URI
to where the dataset is stored.

Installation
------------

Install the dtool lookup server::

    $ pip install dtool-lookup-server

Setup and configuration
-----------------------

Configure the Flask app
^^^^^^^^^^^^^^^^^^^^^^^

The dtool lookup server is a Flask app. Flask needs to know where to look for
the app. One therefore needs to define the ``FLASK_APP`` environment variable::

    $ export FLASK_APP=dtool_lookup_server

Configure the SQL database
^^^^^^^^^^^^^^^^^^^^^^^^^^

The dtool lookup server stores administrative metadata in a SQL database.
By default it uses a SQLite database. However, this can be configured by
setting the ``SQLALCHEMY_DATABASE_URI``, i.e using something along the lines of::

    export SQLALCHEMY_DATABASE_URI=mysql://username:password@server/db

For more information see `flask-SQLAlchemy
<http://flask-sqlalchemy.pocoo.org>`_.

Versioning of the relational database is handled using
`flask-Migrate <https://flask-migrate.readthedocs.io>`_

Populate the SQL database with tables using the commands below::

    $ flask db init
    $ flask db migrate
    $ flask db upgrade

Configure the Mongo database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The dtool lookup server stores descriptive data in a Mongo database. This is
used for free text searching.

Create a directory where the MongoDB data will be stored::

    $ mkdir data

Start Mongo DB, for example using docker::

    $ docker run -d -p 27017:27017 -v `pwd`/data:/data/db mongo


Configure a public and private key pair
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The dtool lookup server implements authentication using JSON Web Tokens.
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

Start the flask app
^^^^^^^^^^^^^^^^^^^

    $ flask run


Populating the dtool lookup server using the CLI
------------------------------------------------

Indexing a base URI
^^^^^^^^^^^^^^^^^^^

Adding a user and managing permissions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Creating an admin user
^^^^^^^^^^^^^^^^^^^^^^


The dtool lookup server API
---------------------------

Standard user usage
^^^^^^^^^^^^^^^^^^^

Looking up URIs based on a dataset's UUID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Listing all datasets
~~~~~~~~~~~~~~~~~~~~


Searching for specific datasets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Getting information about one's own permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Data champion user usage
^^^^^^^^^^^^^^^^^^^^^^^^

Registering a dataset
~~~~~~~~~~~~~~~~~~~~~


Admin user usage
^^^^^^^^^^^^^^^^

Registering a base URI
~~~~~~~~~~~~~~~~~~~~~~

Listing registered base URIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Registering users
~~~~~~~~~~~~~~~~~

Listing registered users
~~~~~~~~~~~~~~~~~~~~~~~~

Updating the permissions on a base URI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Getting informations about the permissions on a base URI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
