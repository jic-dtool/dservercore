Dtool Lookup Server
===================

Dtool Lookup Server is an application that given a dataset UUID returns a URI
to where the dataset is stored.

Create a directory where the MongoDB data will be stored::

    mkdir data

Start Mongo DB in docker::

    docker run -d -p 27017:27017 -v ~/data:/data/db mongo

Start the Flask app::

    export FLASK_APP=app/__init__.py
    flask run
