CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.

[0.21.0]
--------

Added
^^^^^

- return dataset size and item number in dataset schemas
- yield size in bytes information with user-wise summary

[0.20.2]
--------

Added
^^^^^

- Automated github release
- Zenodo integration
- Trusted publishing on PyPI

[0.20.1]
--------

Changed
^^^^^^^

- Changed URLs from ``livMatS`` prefix to ``jic-dtool`` prefix.

[0.20.0]
--------

Changed
^^^^^^^

- Renamed from ``dtool-lookup-server`` to ``dservercore``

[0.19.0] - 2024-06-12
---------------------

Added
^^^^^

- Sorting mechanism in analogy to ``flask_smorest``'s Pagination mechanism
- Deletion, put, and patch routes
- ``/tags`` tag retrieval route

Changed
^^^^^^^

- All routes refactored to adhere to a few simple REST API conventions from "Mark Masse, REST API Design Rulebook, O'Reilly Media, Inc., 2011", namely
   - Forward slash separator indicates hierarchical relationship,
     and URI path conveys the REST API's resource model,
     e.g. ``/users/test-user``, ``/base-uris/smb/test-share``, ``/uris/s3/test-bucket/aad1c62b-b184-422b-841e-ac68eda26fe7``
   - Hyphens used to improve readability and underscores avoided in URIs,
     e.g. ``/base-uris`` instead of ``/base_uris``
   - Plural nouns are used for collections, e.g. ``/users``, ``/base-uris``
   - Singular nouns are used for specific documents, e.g. ``/users/test-user/summary``
   - Query component of a URI used to filter collections, e.g. ``/uris?creator_usernames=test-user&free_text=apple``
   - Query component of URI used to paginate and sort collections , e.g. ``/users?page=2&page_size=5&sort=is_admin,-username``
- use HTTP methods GET, PUT, DELETE for managing resources in the sense of https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods:
   - GET retrieves a resource, e.g. GET ``/users/test-user``
   - PUT registers a resource or replaces an existing resource and behaves idempotent,
     e.g. PUT ``/users/test-user`` will create the user ``test-user`` or replace them if already existing
   - DELETE removes a resource from dserver
- use HTTP response codes to transparently indicate errors in the sense of https://developer.mozilla.org/en-US/docs/Web/HTTP/Status, e.g.
   - 200 OK, Request succeeded, e.g. used by
      - GET to indicate the resource has been fetched and transmitted,
      - PUT to indicate an existing resource has been updated successfully,
      - DELETE to indicate successful removal of a resource
   - 201 Created, The request succeeded, and a new resource was created as a result,
     e.g. used by PUT if the resource had not existed before the request and has been newly created
   - 400 Bad Request, e.g. a dataset to be registered is not valid.
   - 401 Unauthorized, semantically this response means "unauthenticated",
     e.g. user needs to authenticate to access the resource.
   - 403 Forbidden, client does not have access rights to the content,
     e.g. user is authenticated and known to the server, but lacks admin rights to access the specified resource
   - 404 Not Found, server cannot find the requested resource,
     e.g. user is authenticated and has permissions to search a specific base URI, but no dataset entry exists for the requested URI

Deprecated
^^^^^^^^^^


Removed
^^^^^^^


Fixed
^^^^^


Security
^^^^^^^^


[0.18.0] - 2023-08-13
---------------------


Added
^^^^^

- Integrated openapi
- Pagination for all listing endpoints
- Defined schemas for endpoint arguments
- Missing and improved docstrings for endpoints
- Replaces get_json() uses for the use of request's arguments
- Flask CLI commands for inspecting app configuration
- ``/config/versions`` route
- Entrypoints ``extensions``, ``search``, ``retrieve`` for plugins
- Abstract base classes for plugins
- Plugins provied a metho ``get_config_secrets_to_obfuscate`` that tells the core app which configuration parameters are not to be reported clear text
- Sample ``wsgi.py`` script for wrapping Flask app and dumping all HTTP requests and responses

Changed
^^^^^^^

- The frozen_at and created_at fields for /dataset/register endpoint are string representation of the floating point
  value. Previously the application was permissive and accepted any integer, float or string type. The type sanitation
  shall happen in the API client.
- When registering a dataset the readme should now be provided as a string
  (text) rather than as a dictionary of key value entries
- The ``/config/info`` route now provides a dump of the actual Flask app config
- Expose ``X-Pagination`` headers per default.


Removed
^^^^^^^

- ``plugins`` entrypoint



[0.17.2] - 2021-05-17
---------------------

Fixed
^^^^^

- Made code compatible with flask-jwt-extended version 4 API
  https://github.com/jic-dtool/dservercore/issues/19
- Resolve SQLAlchemy warnings about conflicting relationships
  https://github.com/jic-dtool/dservercore/issues/20
- Resolve SQLAlchemy warning about cartesian product



[0.17.1] - 2021-05-12
---------------------

Fixed
^^^^^

- Fixed version of flask-jwt-extended to be less than 4 to fix
  https://github.com/jic-dtool/dservercore/issues/19


[0.17.0] - 2021-03-15
---------------------

Improved user management.

Added
^^^^^

- Added ``flask user delete`` CLI command
- Added ``flask user update`` CLI command
- Added ``dtool_lookup_server.utils.delete_users`` helper function
- Added ``dtool_lookup_server.utils.update_users`` helper function


[0.16.0] - 2020-11-23
---------------------

Changed
^^^^^^^

- Moved ``iter_datasets_in_base_uri`` from ``dtool_lookup_server.utils`` to ``dtoolcore``

Fixed
^^^^^

- Fixed issues registering datasets with "too much" metadata, resulting in datasets
  information JSON documents that were too large for the mongo database. These datasets
  are now ignored. See
  `issue 16 <https://github.com/jic-dtool/dservercore/issues/16>`_
  for more information:



[0.15.0] - 2020-10-15
---------------------

This release makes it possible to create plugins to the dtool-lookup-server!

Many thanks to `Johannes L. H�rmann <https://github.com/jotelha>`_ and `Lars
Pastewka <https://github.com/pastewka>`_ for bug reports, design discussions
and code contributions.

Added
^^^^^

- Added hook to allow the loading of plugins. Scaffold code for implementing a
  plugin can be found in
  https://github.com/livMatS/dserver-plugin-scaffolding.
  For examples of actual plugins see:
  https://github.com/livMatS/dserver-dependency-graph-plugin
  and
  https://github.com/livMatS/dserver-plugin-scaffolding
- Added /config route; see
  https://github.com/jic-dtool/dservercore/pull/6
- Added ability to filter searches by UUID by supplying ``uuids`` keyword and list of
  UUIDs of interest to a query submitted to the /dataset/search route; see
  https://github.com/jic-dtool/dservercore/pull/8
- Added dtool_lookup_server.utils.preprocess_query_base_uris helper function; see
  https://github.com/jic-dtool/dservercore/pull/7 and
  https://github.com/jic-dtool/dservercore/issues/10

Fixed
^^^^^

- Fixed timestamps returned form /dataset/search route; they are now returned
  as floats rather than as strings; see
  https://github.com/jic-dtool/dservercore/issues/3
- Fixed defect in ``flask user token`` CLI command when using python3; see
  https://github.com/jic-dtool/dservercore/pull/5


[0.14.1] - 2020-04-02
---------------------

Fixed
^^^^^

- Made /dataset/summary route able to cope with individual datasets in the
  mongo database missing the tags key


[0.14.0] - 2020-04-01
---------------------

Added
^^^^^

- Added "tags" and "datasets_per_tag" keys to JSON response from
  /dataset/summary route
- Added ability to filter/search based on tags


Changed
^^^^^^^

- Registering a dataset now requires a key for ``tags`` in the JSON
  content


[0.13.0] - 2020-03-10
---------------------

Added
^^^^^

- Added /dataset/annotations route to which one can POST a URI and get back the
  associated dataset annotations


Changed
^^^^^^^

- Registering a dataset now requires a key for ``annotations`` in the JSON
  content
- The /dataset/search route no longer returns manifest and readme in the body
  of the JSON response. These will now have to be retrieved using the
  /dataset/manifest and /dataset/readme routes respectively. This change was
  implemented to overcome the slow response time when accessing many (>1000)
  datasets using the /dataset/search route. 

Fixed
^^^^^

- Made registration of datasets more tolerant to type of frozen_at in
  admin_metadata, now accepts value as a string


[0.12.0] - 2020-02-27
---------------------

Added
^^^^^

- Added /dataset/manifest route to which one can POST a URI and get back the
  associated dataset manifest
- Added /dataset/readme route to which one can POST a URI and get back the
  associated dataset readme


[0.11.0] - 2019-07-08
---------------------

Added
^^^^^

- Ability to log request headers in debug mode


[0.10.0] - 2019-06-14
---------------------

Changed
^^^^^^^

- Added logic to config.Config that ignores ``JWT_PRIVATE_KEY_FILE`` and
  ``JWT_PUBLIC_KEY_FILE`` if ``JWT_PUBLIC_KEY`` is set in the environment.
  This makes it easier to configure the ``dtool-lookup-server`` to make use
  of tokens generated from another server. In other words where the private
  key file is maintained in a different service.


[0.9.0] - 2019-06-06
--------------------

Changed
^^^^^^^

- Improved the JSON query format when sending POST requests to the
  /dataset/search route


[0.8.0] - 2019-06-03
--------------------

Added
^^^^^

- Added "/dataset/summary" route with summary information about the datasets
  accessible to a user
- Added the manifest structural metadata to the MongoDB


[0.7.1] - 2019-05-09
--------------------

- Made "/dataset/register" route more robust when "created_at" is a
  string as opposed to a floating point value


[0.7.0] - 2019-05-09
--------------------

Added
^^^^^

- Added ``frozen_at`` column to admin metadata stored in SQL table
- Added ``created_at`` column to admin metadata stored in SQL table
- Added Ansible provisioning script to git repository


Changed
^^^^^^^

- ``dtool_lookup_server.utils.dataset_info_is_valid()`` helper function now
  returns false if "frozen_at" is missing.


Fixed
^^^^^

- Made /dataset/register route more robust if base URI has not been registered



[0.6.0] - 2019-05-02
--------------------

Added
^^^^^

- Added support for Cross Origin Resource Sharing (CORS), making cross-origin
  AJAX possible
- Added ``creator_username`` column to admin metadata stored in SQL table


Changed
^^^^^^^

- ``dtool_lookup_server.utils.dataset_info_is_valid()`` helper function now
  return s false if "creator_username" is missing.
 

[0.5.0] - 2019-04-01
--------------------

Added authentication and authorization!

Added
^^^^^

New and replacement routes.

- /admin/base_uri/list
- /admin/base_uri/register
- /dataset/list
- /dataset/lookup/<uuid>
- /dataset/register
- /dataset/search
- /admin/permission/info
- /admin/permission/update_on_base_uri
- /user/info/<username>
- /admin/user/list
- /admin/user/register

Flask CLI utilities for managing dserver.

- ``flask base_uri add``
- ``flask base_uri index``
- ``flask base_uri list``
- ``flask user add``
- ``flask user list``
- ``flask user register_permission``
- ``flask user search_permission``
- ``flask user token``

Removed
^^^^^^^

All previous routes.

- /register_dataset route
- /lookup_datasets route
- /search_for_datasets route


[0.4.0] - 2018-08-09
--------------------

Added
^^^^^

- Add ability to update a record
- Add inclusion of descriptive metadata from README to mass_registration.py
  script
- Add entire document wild card search indexing


[0.3.0] - 2018-03-06
--------------------

Added
^^^^^

- Ability to mass register datasets from a base URI


[0.2.0] - 2018-03-06
--------------------

Added
^^^^^

- Ability to search for datasets


[0.1.0] - 2018-03-02
--------------------

Initial release

Added
^^^^^

- Ability to view the number of registered datasets
- Ability to register a dataset
- Ability to access the copies of a dataset associated with a UUID
