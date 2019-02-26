Draft Specification
===================

:Date: 21 February 2019
:Author: Tjelvar Olsson

Introduction
------------

*This is a draft!*

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
  privileges register datasets on a base URI so that they can register datasets
  from that base URI
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
      -d '["bashful", "doc", "dopey", "happy", "grumpy", "sleepy", "sneezy"]'  \
      https://localhost:5000/user/register

The Magic Mirror admin then tries to register the huntsman as a single user::

    $ curl \
      -H "Content-Type: application/json"  \
      -X POST  \
      -d '"huntsman"'  \
      https://localhost:5000/user/register

Since, this is a string rather than an array the lookup server returns ``400
Bad Request``.

The Magic Mirror admin then corrects the request by using an array instead of a
string::

    $ curl \
      -H "Content-Type: application/json"  \
      -X POST  \
      -d '["huntsman"]'  \
      https://localhost:5000/user/register

To ensure that all seven dwarfs and the huntsman have been added the Magic
Mirror lists all the users registered in the lookup server::

    $ curl https://localhost:5000/user/list
    ["bashful", "doc", "dopey", "happy", "huntsman", "grumpy", "sleepy", "sneezy"]

Technical details
-----------------

Questions
^^^^^^^^^

- What is the difference between a token based authentication system and basic auth?
- Does ``curl`` support token based authentication?
- Which authentication system should be used?
- What database is most suitable for managing users? NoSQL vs SQL...
- What database is best for searching for metadata? NoSQL vs SQL...
- What Python web framework should be used? Flask vs Pyramid vs Django?

Requirements
^^^^^^^^^^^^

- The lookup server must be accessible to clients on the network, i.e. it
  should be a web server
- Scripts and applications should be able to interact with the lookup server
  through an API
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
- As well as the API the lookup server will have a basic web (HTML) interface
  allowing standard users to list and search for datasets

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


Permission management
~~~~~~~~~~~~~~~~~~~~~

``/permission/update_permissions_for_specific_user_on_base_uri``:

    POST to give a update a specific user's permissions a base URI. Only admin allowed.

    Grant Grumpy search privileges on the snow-white bucket::

        {"user": "grumpy", "base_uri": "s3://snow-white", "permissions": ["search"]}

    Grant Sleepy search and register privileges on the snow-white bucket::

        {"user": "sleepy", "base_uri": "s3://snow-white", "permissions": ["search", "register"]}

    Revoke all Dopey's  privileges on the snow-white bucket::

        {"user": "dopey", "base_uri": "s3://snow-white", "permissions": []}

    Server responds with ``200 OK`` if successful. Server responds with ``409 Conflict`` if
    either the username or the base URI does not exist in the lookup server.

``/permission/update_all_permissions_on_base_uri``:

    POST to give update a all permissions on a base URI. Only admin allowed.

    Revoke all users privileges::

        {"users_with_search_permissions": [],
         "users_with_register_permissions": [],
         "base_uri": "s3://snow-white"}

    Give Grumpy, Dopey permission to search and Sleepy permission to register datasets::

        {"users_with_search_permissions": ["grumpy", "dopey"],
         "users_with_register_permissions": ["sleepy"],
         "base_uri": "s3://snow-white"}


User stories
------------

This user story uses many raw ``curl`` requests to the REST API for
illustrative purposes. In practice one would write helper scripts that called
the REST API.

The admin user tries to add a standard user called ``grumpy``::

    $ curl \
        -u ${BASIC_AUTH_HEADER}  \
        -H "Content-Type: application/json"  \
        -X POST  \
        -d '{
            "username":"grumpy",
            "email":"grumpy@mr-men.com"}'  \
        https://localhost:5000/add_user

The admin user has forgotten to configure the ``BASIC_AUTH_HEADER`` environment
variable and gets a ``401 Unauthrized`` status response.

The admin user sets the ``BASIC_AUTH_HEADER`` and  tries again.  The server
responds with ``201 Created``. The user is added to the lookup server and the
user is emailed a one time password and a link to a web page for changing the
password. The user updates the password.

The admin user accidentally submits the POST request to add the ``grumpy`` user
again. The server responds with ``409 Conflict``

The ``grumpy`` user should be authorized to search the datasets stored in the
``s3://mr-men`` and the ``azure://snow-white`` buckets. First of all these base
URIs need to be registered with the lookup server. The admin user adds the
``s3://mr-men`` base URI first::

    $ curl \
        -u ${BASIC_AUTH_HEADER}  \
        -H "Content-Type: application/json"  \
        -X POST  \
        -d '{"base_uri": "s3://mr-men"}'  \
        https://localhost:5000/add_base_uri

The server responds with ``201 Created``.  The admin user accidentally submits
the POST request to add the ``s3://mr-men`` base URI again. The server responds
with ``409 Conflict``. The admin user then adds the ``azure://snow-white`` base
URI::

    $ curl \
        -u ${BASIC_AUTH_HEADER}  \
        -H "Content-Type: application/json"  \
        -X POST  \
        -d '{"base_uri": "azure://snow-white"}'  \
        https://localhost:5000/add_base_uri

The admin user indexes the lookup server using the ``mass_registration.py`` script::

    python mass_registration.py s3://mr-men

This pulls out relevant information from the datasets in the base URL and makes
requests along the lines of the below::

    $ curl \
        -u ${BASIC_AUTH_HEADER}  \
        -H "Content-Type: application/json"  \
        -X POST  \
        -d '{
            "uri":"s3://mr-men/af6727bf-29c7-43dd-b42f-a5d7ede28337",
            "uuid":"af6727bf-29c7-43dd-b42f-a5d7ede28337",
            "type":"dataset"}'  \
        http://localhost:5000/register_dataset

For each of these requests the server responds with ``201 Created``.  If the
base URI had not been registered before the server would have responded with
``409 Conflict``.

The admin user then adds ``grumpy`` to the ``s3://mr-men`` by running the
command::

    $ curl \
        -u ${BASIC_AUTH_HEADER}  \
        -H "Content-Type: application/json"  \
        -X POST  \
        -d '{
            "username":"grumpy",
            "base_uri": "s3://mr-men"
            }'  \
        http://localhost:5000/give_user_access_to_base_uri

The server responds with ``200 OK``. The admin runs a similar command to add
``grumpy`` to the ``azure://snow-white`` base URI.

The user can now search for datasets. When the ``grumpy`` user makes a search
hits from the ``s3://mr-men`` and ``azure://snow-white`` base URIs are
returned.

The user ``sleepy`` has only had the ``azure://snow-white`` base URI added to
him. When the ``sleepy`` user makes searches the lookup server only hits from
the ``azure://snow-white`` base URI are returned.

The admin also adds the user ``dopey`` to the system. Shortly after the admin
gets an email from ``dopey`` asking for help logging into the system as he has
forgotten the password. The admin user runs the command::

    $ curl \
        -u ${BASIC_AUTH_HEADER}  \
        -H "Content-Type: application/json"  \
        -X POST  \
        -d '{
            "username": "dopey"
            }'  \
        http://localhost:5000/reset_password

The ``dopey`` user is emailed a one time password and a link to a web page for
changing the password.
