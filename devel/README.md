# Development setup

Helper components of a simple development setup.

Provide necessary services with docker composition `docker/env.yml`. 
See `docker/README.md`.

`env.rc` provides flask app configuration in form of environment varables.

`create_test_data.sh` creates test data sets and copis them to test s3 bucket.

`init.sh` prepares the lookup server.

`run.sh` launches the lookup server with `gunicorn`.

# Example envrionment

Create a virtual environment with

```bash
python3 -m venv vev
source venv/bin/activate

pip install gunicorn psycopg2 setuptools_scm
pip install -r requirements.txt
pip install dtool-cli dtool-info dtool-create dtool-s3
pip install git+https://github.com/jotelha/dtool-lookup-server-retrieve-plugin-mongo.git@main
pip install git+https://github.com/jotelha/dtool-lookup-server-search-plugin-mongo.git@main
pip install git+https://github.com/livMatS/dtool-lookup-server-direct-mongo-plugin.git@main
pip install git+https://github.com/livMatS/dtool-lookup-server-dependency-graph-plugin.git@main
pip install git+https://github.com/livMatS/dtool-lookup-server-notification-plugin.git@main
```

and launch server with

```bash
source devel/env.rc
bash devel/init.sh
bash devel/run.sh
```

## On Ubunu (20.04)

To run server with PostgreSQL, instal dependencies 

```
sudo apt install libpq-dev
pip install gunicorn psycopg2
pip install -r requirements.txt 
pip install dtool-s3
```
