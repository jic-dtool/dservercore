Draft Specification
===================

:Date: 21 February 2019
:Author: Tjelvar Olsson

Introduction
------------

*This is a draft!*

When a base URI contains many datasets commands such as ``dtool ls <BASE_URI>``
can take a long time to complete. It would be good to have a means to query
data quicker.  Furthermore it would be great to be able to have a system that
could be used to search the metadata to find relevant datasets.

Technical details
-----------------

Requirements
^^^^^^^^^^^^

- The lookup server must be accessible to clients on the network, i.e. it
  should be a web server
- Scripts and applications should be able to interact with the lookup server
  through an API, maybe a RESTful API
- Users should only be able to find metadata and URIs of datasets that live in
  base URIs that they have been given access to, as such the server needs to
  include authentication and authorisation
- There should be three types of user roles: standard, data champion and admin
  user roles
- A standard user is only able to search the lookup server for datasets in base
  URIs that he/she has access to
- A data champion user is also able to register datasets from base URIs that
  he/she has been given access to
- An admin user can create users and set their roles
- An admin user can add a base URI to the system
- An admin user can associate base URIs with a user to give that user access to
  search those base URIs for metadata and dataset URIs
- The lookup server should be able to manage authorisation itself
- The lookup server should be able to delegate authorisation to an LDAP server
- As well as the API the lookup server will have a basic web (HTML) interface
  allowing standard users to list and search for datasets

Routes
^^^^^^

``/``: HTML web application

``/login``: POST request to login

``/logout``: POST request to logout

``/dataset/lookup/<UUID>``: GET request to list locations where the dataset can be found.

``/dataset/search``: POST request to list datasets found by search query.

``/dataset/register``: POST request to register a dataset. Only admin and data champion allowed.

``/user/create``: POST to create a user. Only admin allowed.

``/user/base_uri_search``: POST to give/remove a user's permissions to search on a base URI. Only admin allowed.

``/user/base_uri_register``: POST to give/remove a user's permissions to register datasets on a base URI. Only admin allowed.

``/user/info/<USERNAME>``: GET request for user details. Only admin and user in question allowed.

``/base_uri/register``: POST request to register a base URI. Only admin allowed.



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
