Draft Specification
===================

.. |date| date::

:Author: Tjelvar Olsson
:Date: |date|
:Status: Draft

Introduction
------------

When a base URI contains many datasets commands such as ``dtool ls <BASE_URI>``
can take a long time to complete. It would be good to have a means to query
data quicker.  It would also be great to be able to have a system that
could be used to search the metadata to find relevant datasets.
Finally, it would be fantastic to have a web interface to list and search for
datasets.

High level user stories
-----------------------

- As a bioinformatician I want to be able to use free text search so that I can
  find URIs of datasets of interest to me.
- As a bioinformatician I want to be able to retrieve all URIs of a dataset with
  a specific UUID so that I can decide which URI to use in my processing pipeline
- As a project leader I want to be able to use a web browser to view all the
  datasets my group has pushed to the object storage so that I can
  reassure myself that the data is safe and secure
- As a systems administrator I want to be able to add users to the lookup server
- As a systems administrator I want to be able to give a user
  privileges to search for datasets in a base URI so that they can find datasets
  from that base URI
- As a systems administrator I want to be able to give a user
  privileges to register datasets on a base URI so that they can register
  datasets from that base URI
- As a data champion, a user with privileges to register datasets, I want to be
  able to re-index a base URI when new datasets have been uploaded to the base
  URI

Detailed user story
-------------------

The lookup server has been configured and it contains a single admin user.  The
admin user, fondly known as Magic Mirror,  starts off by registering a base
URI with the lookup server::

    $ curl \
        -H "Content-Type: application/json"  \
        -X POST  \
        -d '{"base_uri": "s3://snow-white"}'  \
        https://localhost:5000/base_uri/register

The Magic Mirror admin user then registers the seven dwarfs as standard users
of the lookup server::

    $ curl \
      -H "Content-Type: application/json"  \
      -X POST  \
      -d '[
        {"name": "bashful", "email": "bashful@disney.com"}, 
        {"name": "doc", "email": "doc@disney.com"},
        {"name": "dopey", "email": "dopey@disney.com},
        {"name": "happy", "email": "happy@disney.com},
        {"name": "grumpy", "email" "grumpy@disney.com"},
        {"name": "sleepy", "email": "sleepy@disney.com"},
        {"name": "sneezy", "email": "sneezy@disney.com"}
      ]'  \
      https://localhost:5000/user/register

The Magic Mirror admin then tries to register Snow White as a single user::

    $ curl \
      -H "Content-Type: application/json"  \
      -X POST  \
      -d '{"name: "snow-white", "email": "snow-white@disney.com"}'  \
      https://localhost:5000/user/register

Since, this is a dictionary rather than a list of dictionaries the lookup
server returns ``400 Bad Request``.

The Magic Mirror admin then corrects the request by using a list of
dictionaries instead of a dictionary::

    $ curl \
      -H "Content-Type: application/json"  \
      -X POST  \
      -d '[{"name: "snow-white", "email": "snow-white@disney.com"}]'  \
      https://localhost:5000/user/register

To ensure that all seven dwarfs and the Snow White have been added the Magic
Mirror lists all the users registered in the lookup server::

    $ curl https://localhost:5000/user/list
    ["bashful", "doc", "dopey", "happy",
     "grumpy", "sleepy", "sneezy", "snow-white"]

At this point all the dwarfs and Snow White have been sent an email with a link
to a one time login password.

The Magic Mirror now wants to give Snow White permissions to register datasets
stored in the ``s3://snow-white`` bucket and for all users to be able to search
for datasets that have been registered from this base URI::

    $ curl \
      -H "Content-Type: application/json"  \
      -X POST  \
        {
          "users_with_search_permissions": [
            "bashful",
            "doc",
            "dopey",
            "happy",
            "grumpy",
            "sleepy",
            "sneezy",
            "snow-white"
          ]
          "users_with_register_permissions": ["snow-white],
          "base_uri": "s3://snow-white"
        }
      https://localhost:5000/permission/update_all_permissions_on_base_uri

Snow White logs in, updates her password using the web interface and obtains an
authentication token. She then registers all the datasets in the
``s3://snow-white`` bucket using the ``mass_registration.py`` script::

    python mass_registration.py s3://snow-white

This script loops over all the datasets in the ``s3://snow-white`` bucket and constructs
HTTP POST requests along the lines of that below::

    $ curl \
      -H "Content-Type: application/json"  \
      -X POST  \
        {
          "base_uri": "s3://snow-white",
          "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337",
          "uri": "s3://snow-white/af6727bf-29c7-43dd-b42f-a5d7ede28337",
          "type": "dataset",
          "created_at": 1536236399.19497,
          "frozen_at": 1536238185.881941,
          "dtoolcore_version": "3.6.0",
          "creator_username": "dopey",
          "name": "red.apples",
          "readme": {"description": "lots of bad apples"}
        }
      https://localhost:5000/dataset/register

One of the dwarfs, who is looking very sleepy, then tries to search for
datasets using the term ``apple``::

    $ curl https://localhost:5000/dataset/list?any=apple

Then the sleepy dwarf looks for all datasets created by ``dopey``::

    $ curl https://localhost:5000/dataset/list?creator_username=dopey

Then the sleepy dwarf looks for all datasets created by ``dopey`` with the term
``apple``::

    $ curl https://localhost:5000/dataset/list?creator_username=dopey&any=apple

The dopey dwarf also wants to search for datasets. However, he has forgotten his
new password. He therefore sends a request to generate another one time login
password::

    $ curl \
      -H "Content-Type: application/json"  \
      -X POST  \
        {
          "user": "dopey"
        }
      https://localhost:5000/reset_password

.. raw:: pdf

   PageBreak

Technical details
-----------------

Requirements
^^^^^^^^^^^^

- The lookup server must be accessible to clients on the network, i.e. it
  should be a web server
- The lookup server must be served over HTTPS
- Scripts and applications should be able to interact with the lookup server
  through an API, both in terms of searching for datasets and managing users
  and what base URIs the users are authenticated to work with
- Users should only be able to find metadata and URIs of datasets that live in
  base URIs that they have been given access to, as such the server needs to
  include authentication and authorisation
- There are two types of users: standard and admin
- A standard user is granted permissions on base URIs by an admin user
- There are two types of permissions a standard user can be granted on a base URI:
  search and register
- Search permissions allow a standard user to search the lookup server for
  datasets in the base URI
- Register permissions allow a standard user to register datasets from the base URI
- An admin user can create users
- An admin user can add a base URI to the system
- An admin user can grant a user permissions on a base URI
- The lookup server should be able to manage authorisation itself
- The lookup server should be able to delegate authorisation to an LDAP server
- As well as the API the lookup server will have a web (HTML) interface
  allowing standard users to list and search for datasets

Authentication
^^^^^^^^^^^^^^

The lookup server needs to manage users. In it's most basic form users and
their hashed passwords will be stored in a relational database. However, there
will be a setting to enable LDAP pass through authentication. Once a user is
registered in the system it will be possible for him/her to request a JSON Web Token.
Using this token the user is able to authenticate against the lookup server.

- `Web Authentication Methods Explained <https://blog.risingstack.com/web-authentication-methods-explained/>`_
- `The Ins and Outs of Token Based Authentication <https://scotch.io/tutorials/the-ins-and-outs-of-token-based-authentication>`_
- `5 Easy Steps to Understanding JSON Web Tokens <https://medium.com/vandium-software/5-easy-steps-to-understanding-json-web-tokens-jwt-1164c0adfcec>`_

Databases
^^^^^^^^^

The lookup server will manage several different pieces of information
including: users, base URIs, user to base URI relationships, dataset
administrative data, and dataset descriptive metadata.

A relational database, such as MySQL, is the best option for managing
structured data and relationships. As such it will be used to manage:

- Users
- Base URIs
- User to base URI relationships
- Dataset administrative data (base_uri, uuid, uri, created_at,
  frozen_at, dtoolcore_version, creator_username, name)

A NoSQL document database, such as MongoDB, is the best option for managing
unstructured data. As such it will be used to manage:

- Dataset descriptive metadata

Further reading:

- `Hybrid Databases: Combining Relational and NoSQL <https://www.stratoscale.com/blog/dbaas/hybrid-databases-combining-relational-nosql/>`_
- `Should You Use NoSQL Or SQL Db Or Both? <https://medium.com/swlh/should-you-use-nosql-or-sql-db-or-both-349cb26c9add>`_

Python web framworks
^^^^^^^^^^^^^^^^^^^^

There are several popular Python web frameworks including Django, Pyramid and
Flask.

Django is popular because it has built in user management. However, this system
is based on sessions and cookies rather than JSON web token and as such it does
not give much.  Django makes use of its own object relational mapper rather
then the more generic Python library SQLAlchemy. Django does not have any
support for working with other databases such as MongoDB.

Pyramid markets itself as a web framework that can scale from small to big.
It has support for JWT, LDAP, SQLAlchemy, MongoDB. However, it does not have
an out of the box solution for managing users. Also, there seems to be fewer
tutorials and ways to learn about Pyramid than Django and Flask.

Flask markets itself as a micro framework. It seem like the best fit as it supports
JWT, LDAP, SQLAlchemy, MongoDB. Furthermore, it has an extension for user management.
There is plenty of tutorials and documentation describing how to work with Flask.

Initially we will try to use Flask to implement the lookup server. It may be useful
to make use of the tutorials and extensions listed below:

- `JWT authorization in Flask <https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb>`_
- `Token-Based Authentication With Flask <https://realpython.com/token-based-authentication-with-flask/>`_
- `Flask-User <https://flask-user.readthedocs.io/en/latest/>`_
- `Flask LDAP3 Login <https://flask-ldap3-login.readthedocs.io/en/latest/>`_
- `Flask-SQLAlchemy <http://flask-sqlalchemy.pocoo.org/2.3/>`_
- `Flask-PyMongo <https://flask-pymongo.readthedocs.io/en/latest/>`_
- `Testing Flask Applications <http://flask.pocoo.org/docs/1.0/testing/>`_

HTTPS
^^^^^

Let’s Encrypt is a free, automated, and open Certificate Authority.

- `How to Secure Apache with Let's Encrypt on CentOS 7 <https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-centos-7>`_
- `Securing NGINX with SSL using Let’s Encrypt on CentOS 7.x <https://osjournal.com/securing-nginx-with-ssl-using-lets-encrypt-on-centos-7-x-18/>`_
- `Let’s Encrypt <https://letsencrypt.org/>`_

Development tools
^^^^^^^^^^^^^^^^^

- `Postman Simplifies API Development <https://www.getpostman.com/>`_

Suggested routes
^^^^^^^^^^^^^^^^

Web application
~~~~~~~~~~~~~~~

``/``:

    HTML web application


Authentication
~~~~~~~~~~~~~~

``/login``:

    POST request to login

``/logout``:

    POST request to logout

Dataset search and lookup
~~~~~~~~~~~~~~~~~~~~~~~~~

``/dataset/lookup/<UUID>``:

    GET request to list locations where the dataset can be found.

``/dataset/search``:

    POST request to list datasets found by search query.


Base URI management
~~~~~~~~~~~~~~~~~~~

``/base_uri/register``:

    POST request to register a base URI. Only admin allowed.

``/base_uri/list``:

    GET request to list all base URIs a user is authorised to search.


Dataset management
~~~~~~~~~~~~~~~~~~

``/dataset/register``:

    POST request to register a dataset. Only admin and data champions allowed.

``/dataset/list``:

    GET request to list all datasets a user is authorised to view.


User management
~~~~~~~~~~~~~~~

``/user/register``:

    POST request to create/register a user. Only admin allowed.

``/user/list``:

    GET request to list all users. Only admin allowed.

``/user/info/<USERNAME>``:

    GET request for user details, including base URIs that the user has been
    given search and register privileges on. Only admin and user in question
    are allowed.

.. raw:: pdf

   PageBreak

Permission management
~~~~~~~~~~~~~~~~~~~~~

``/permission/update_permissions_for_specific_user_on_base_uri``:

    POST to update a specific user's permissions a base URI. Only admin allowed.

    Grant Grumpy search privileges on the snow-white bucket::

        {
           "user": "grumpy",
           "base_uri": "s3://snow-white",
           "permissions": ["search"]
        }

    Grant Sleepy search and register privileges on the snow-white bucket::

        {
          "user": "sleepy",
          "base_uri": "s3://snow-white",
          "permissions": ["search", "register"]
        }

    Revoke all Dopey's  privileges on the snow-white bucket::

        {"user": "dopey", "base_uri": "s3://snow-white", "permissions": []}

    Server responds with ``200 OK`` if successful. Server responds with ``409 Conflict`` if
    either the username or the base URI does not exist in the lookup server.

``/permission/update_all_permissions_on_base_uri``:

    POST to update all permissions on a base URI. Only admin allowed.

    Revoke all users privileges::

        {"users_with_search_permissions": [],
         "users_with_register_permissions": [],
         "base_uri": "s3://snow-white"}

    Give Grumpy, Dopey permission to search and Sleepy permission to register datasets::

        {"users_with_search_permissions": ["grumpy", "dopey"],
         "users_with_register_permissions": ["sleepy"],
         "base_uri": "s3://snow-white"}
