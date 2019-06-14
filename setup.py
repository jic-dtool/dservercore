from setuptools import setup

url = "https://github.com/jic-dtool/dtool-lookup-server"
version = "0.10.0"
readme = open('README.rst').read()

setup(
    name="dtool-lookup-server",
    packages=["dtool_lookup_server"],
    description="Web API to register/lookup/search for dtool dataset metadata",
    long_description=readme,
    package_data={"dtool_lookup_server": ["templates/*"]},
    include_package_data=True,
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@jic.ac.uk",
    version=version,
    url=url,
    entry_points={
        'flask.commands': [
            'base_uri=dtool_lookup_server.cli:base_uri_cli',
            'user=dtool_lookup_server.cli:user_cli',
        ],
    },
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-migrate",
        "flask-pymongo",
        "flask-cors",
        "dtoolcore",
        "dtool_irods",
        "dtool_s3",
        "dtool_ecs",
        "flask-jwt-extended[asymmetric_crypto]",
        "pyyaml",
    ],
    download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)
