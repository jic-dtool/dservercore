# Development setup

Helper components of a simple development setup.

Provide necessary services with docker composition `docker/env.yml`. 
See `docker/README.md`.

`env.rc` provides flask app configuration in form of environment varables.

`create_test_data.sh` creates test data sets and copis them to test s3 bucket.

`init.sh` prepares the lookup server.

`run.sh` launches the lookup server with `gunicorn`.

## On Ubunu (20.04)

To run server with PostgreSQL, instal dependencies 

```
sudo apt install libpq-dev
pip install gunicorn psycopg2
pip install -r requirements.txt 
pip install dtool-s3
```
