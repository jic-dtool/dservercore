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
