Dtool Lookup Server
===================

Dtool Lookup Server is an application that given a dataset UUID returns a URI
to where the dataset is stored.

Setup and installation
----------------------

Install the dtool lookup server::

    $ python setup.py install

Create a directory where the MongoDB data will be stored::

    $ mkdir data

Start Mongo DB in docker::

    $ docker run -d -p 27017:27017 -v `pwd`/data:/data/db mongo

Start the Flask app::

    $ export FLASK_APP=dtool_lookup_server
    $ flask run

Mass registration
-----------------

This package provides a script for mass registration of all datasets in a
base URI. It can be run with::

    $ python registration_utils/mass_registration.py BASE_URI

The REST API
------------

Initially no datasets have been registered::

    $ curl http://localhost:5000
    0 registered datasets

Register a local dataset::

    $ curl \
        -H "Content-Type: application/json"  \
        -X POST  \
        -d '{
            "uri":"file:///tmp/a_ds",
            "uuid":"af6727bf-29c7-43dd-b42f-a5d7ede28337",
            "type":"dataset"}'  \
        http://localhost:5000/register_dataset

Now there should be one dataset registered::

    $ curl http://localhost:5000
    1 registered datasets

Look up the dataset(s) associated with the registered UUID::

    $ curl http://localhost:5000/lookup_datasets/af6727bf-29c7-43dd-b42f-a5d7ede28337
    [
      {
        "type": "dataset",
        "uri": "file:///tmp/a_ds",
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337"
      }
    ]

Register another copy of the dataset stored in AWS S3 object store::

    $ curl \
        -H "Content-Type: application/json"  \
        -X POST  \
        -d '{
            "uri":"s3:/dtool-test-s3-bucket/af6727bf-29c7-43dd-b42f-a5d7ede28337",
            "uuid":"af6727bf-29c7-43dd-b42f-a5d7ede28337",
            "type":"dataset"}'  \
        http://localhost:5000/register_dataset

Now there are two datasets associated with the registered UUID::

    $ curl http://localhost:5000/lookup_datasets/af6727bf-29c7-43dd-b42f-a5d7ede28337
    [
      {
        "type": "dataset", 
        "uri": "file:///tmp/a_ds", 
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337"
      }, 
      {
        "type": "dataset", 
        "uri": "s3:/dtool-test-s3-bucket/af6727bf-29c7-43dd-b42f-a5d7ede28337", 
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337"
      }
    ]
