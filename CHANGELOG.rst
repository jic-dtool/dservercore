CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.

[Unreleased]
------------

Added
^^^^^


Changed
^^^^^^^


Deprecated
^^^^^^^^^^


Removed
^^^^^^^


Fixed
^^^^^


Security
^^^^^^^^


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

Flask CLI utilities for managing the dtool lookup server.

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
