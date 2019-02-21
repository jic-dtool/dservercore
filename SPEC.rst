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

Programmatic access would most conveniently be through a web server hosted REST
API.

In order to protect metadata such a web server would require an
authentication/authorization mechanism. The lookup server would therefore need
to store users. There would be at least two types of users: standard and admin
users.

Standard users would use the lookup server to search for datasets of interest.

Admin would be able to:

- Add users to the lookup server
- Add base URIs to be indexed to the lookup server
- Re-index a base URI
- Give standard users the ability to search one or more base URIs

In the simplest form the lookup server would manage users, passwords,
authentication and authorization.

In the future the lookup server needs to be able to delegate authentication to
a LDAP server so that standard users don't need to remember another password.

Authentication will be persisted using cookies so that the end user does not
need to type in the password every time the search functionality is used. It is
up to the client to implement the handling the persistance of cookies. In the
case of the dtool CLI this will be done using the dtool config file.

The lookup server is meant to be a piece in a distributed, loosely coupled
dtool eco-system. Access to datasets in AWS S3 is likely to be controlled using
policies on buckets. As such if the group of people with access to that bucket
changes the change should also be reflected in the lookup server. This can only
be achieved if these types of chnages can be made to the lookup server in a
programmatic fashion. I.e. it is anticipated that one would write a wrapper
script that updated both the AWS S3 policy and the lookup server access at the
same time.


User stories
------------

This user story uses many raw ``curl`` requests to the REST API for
illustrative purposes. In practice one would write helper scripts that called
the REST API.

The admin user installs the system using Ansible::

    ansible-playbook -i hosts playbook.yml

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
