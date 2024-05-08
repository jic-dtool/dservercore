User stories that lead to *dserver*-centered additions for the *dtool* ecosystem
################################################################################

Packaging
---------

*“As a systems administrator tasked with installing and evaluating
dserver I want to be able to install a minimal working system using as
few commands, databases and environment variables as possible so that I
can get a proof of concept up and running as quickly as possible.”*

For this purpose, we provide a minimal installable meta-package dserver
`dserver-minimal`_ that consists of the core component `dtool-lookup-server`_,
and MongoDB-based search and retrieve plugin implementations
`dserver-search-plugin-mongo`_ and
`dserver-retrieve-plugin-mongo`_ as the reference
implementations for MongoDB-based search and retrieve plugins and a
`reference container composition`_ to launch a playground instance without
any external dependencies.

Automatic ingestion
-------------------

*“As a systems administrator, I want my dserver instance to register
datasets automatically when they are placed on some centralised storage
infrastructure.”*

S3 object storage systems may send out notifications on the creation of
new objects to the additional routes below. The
`dserver-notification-plugin`_ receives S3 event
notifications from S3-compatible object storage systems and evokes
immediate dataset registration.

POST /webhook/notify
~~~~~~~~~~~~~~~~~~~~~

Notify *dserver* about creation, modification or deletion of a dataset.

POST /webhook/notify/{path}
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notify *dserver* about creation, modification or deletion of a dataset.

Cross-sections through parametric space
---------------------------------------

*“As a researcher, I want to be able to query cross-sections of datasets
along arbitrary, a priori unknown parametric dimensions for efficient
analysis. I haven’t got any training on working with databases and I
don’t want to dive into SQL, but I am familiar with the pythonic
concepts of nested lists and dictionaries for describing my experiments
or simulations.”*

This user story leads to making the content of a dataset’s readme
searchable not only by free text, but by specific fields as long as it’s
written in correct, machine-readable YAML. The
`dserver-direct-mongo-plugin`_ translates the readme
into MongoDB-typical JSON-like documents and allows querying and
aggregating those with the MongoDB query language (MQL) via the
additional routes below. This is illustrated by the use case
“cross-sections through a high-dimensional parametric space” in the main
article.

POST /mongo/aggregate
~~~~~~~~~~~~~~~~~~~~~

Aggregate the datasets a user has access to.

POST /mongo/query
~~~~~~~~~~~~~~~~~

Query datasets a user has access to.

Provenance tracking
-------------------

*“As a researcher, I want to track provenance, meaning I want to
document what other datasets a new dataset has been derived from. I do
this by simply noting source dataset UUIDs in a dataset’s readme under
some specific key, e.g. derived_from. Now, I want to directly find the
provenance graph spanned by all my related datasets.”*

The `dserver-dependency-graph-plugin`_ allows querying such a
provenance graph spanned by configurable UUID fields in the readme. It
introduces the following additional routes:

GET /graph/lookup/{uuid}
~~~~~~~~~~~~~~~~~~~~~~~~

List the datasets within the same dependency graph as <uuid>. If not all
datasets are accessible by the user, an incomplete, disconnected graph
may arise.

POST /graph/lookup/{uuid}
~~~~~~~~~~~~~~~~~~~~~~~~~

List the datasets within the same dependency graph as <uuid>. If not all
datasets are accessible by the user, an incomplete, disconnected graph
may arise.

Python API
----------

*“As a researcher, I want to interact programmatically with dserver. I
don’t know anything about REST APIs and I just want to use import some
Python module for querying my datasets, just as I import dtoolcore.”*

The `dtool-lookup-api`_ package provides a thin Python wrapper
around the core REST API for both synchronous and asynchronous
interaction.

Automation for high-throughput computing
----------------------------------------

*“As a researcher tasked with high-throughput computing, I want to
automate creating, freezing, copying and querying datasets and integrate
such automated tasks within other frameworks such as workflow management
tools of my choice.”*

The Python API of *dtool* makes automated batch creation, freezing and
copying of datasets straight-forward. *dserver*’s REST API and its
dtool-lookup-api Python wrapper introduced here do the same for
interacting with *dserver*. We provide `exemplary tasks`_ for
integrating this functionality within the `FireWorks`_ workflow
management system :cite:`jain2015fireworks`.

Graphical user interface
------------------------

*“As a researcher without any experience in working on the command line
or with Python, I want to create, document, freeze and copy datasets and
interact with the lookup server all in one graphical application.”*

The `dtool-lookup-gui`_ offers an experimental graphical user
interface based on Python and `GTK3`_. The `dtool-lookup-webapp`_
offers a demonstrator web interface for searching the lookup
server based on `vue.js`_ and `bootstrap-vue-next`_.

Demonstrator
------------

*“As someone interested in dtool and dserver, I would like to see a
working demonstrator instance in action without having to set up
anything by myself.”*

https://demo.dtool.dev exposes a *dtool-lookup-server* demonstrator
instance with autogenerated OpenAPI RESTful API documentation accessible
via https://demo.dtool.dev/lookup/doc/redoc or
https://demo.dtool.dev/lookup/doc/swagger. Latter web page offers the
interactive testing of requests against authorization by token. A token
can, for example, be generated by

.. code-block::bash

   curl --insecure -H "Content-Type: application/json" \
      -X POST -d '{"username": "testuser", "password": "test_password" }' \
      https://demo.dtool.dev/token

.. _dserver-minimal: https://github.com/livMatS/dserver-minimal
.. _dtool-lookup-server: https://github.com/jic-dtool/dtool-lookup-server
.. _dserver-notification-plugin: https://github.com/livMatS/dserver-notification-plugin
.. _dserver-search-plugin-mongo: https://github.com/livMatS/dserver-direct-mongo-plugin
.. _dserver-retrieve-plugin-mongo: https://github.com/livMatS/dserver-direct-mongo-plugin
.. _reference container composition: https://github.com/livMatS/dserver-container-composition
.. _dserver-direct-mongo-plugin: https://github.com/livMatS/dserver-direct-mongo-plugin
.. _dserver-dependency-graph-plugin: https://github.com/livMatS/dserver-dependency-graph-plugin
.. _dtool-lookup-api: https://github.com/livMatS/dtool-lookup-api
.. _exemplary tasks: https://github.com/IMTEK-Simulation/imteksimfw
.. _FireWorks: https://materialsproject.github.io/fireworks/
.. _dtool-lookup-gui: https://github.com/livMatS/dtool-lookup-gui
.. _GTK3: https://docs.gtk.org/gtk3
.. _dtool-lookup-webapp: https://github.com/livMatS/dtool-lookup-webapp
.. _vue.js: https://vuejs.org/
.. _bootstrap-vue-next: https://github.com/bootstrap-vue-next/bootstrap-vue-next

