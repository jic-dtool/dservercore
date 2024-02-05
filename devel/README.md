# Development setup

For development, it will be helpful to run the `dserver` app directly from within the repository root.

The folder `devel` contains helper components to set up a simple development setup.

To run a meaningful `dserver` instance, underlying services like databases and storage infrastructure are necessary.

The docker composition within `docker/env.yml` provides a collection of such services. See `docker/README.md`.

`dtool.json` provides a minimal configuration for a lookup server launched as
described in the following. Place it at `${HOME}/.config/dtool/dtool.json`.

`env.rc` provides flask app configuration in form of environment varables.

`create_test_data.sh` creates test data sets and copis them to test s3 bucket.

`init.sh` prepares the lookup server.

`run.sh` launches the lookup server with `gunicorn`.

## Example environment

Create a virtual environment with

```bash
python3 -m venv venv
source venv/bin/activate

pip install gunicorn psycopg2 setuptools_scm wheel
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

## Ubuntu (20.04)

To run server with PostgreSQL, install dependencies 

```
sudo apt install libpq-dev
pip install gunicorn psycopg2
pip install -r requirements.txt 
pip install dtool-s3
```
