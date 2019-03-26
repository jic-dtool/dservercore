from setuptools import setup

setup(
    name="dtool-lookup-server",
    packages=["dtool_lookup_server"],
    include_package_data=True,
    package_data={"dtool_lookup_server": ["templates/*"]},
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
        "dtoolcore",
        "dtool_irods",
        "dtool_s3",
        "dtool_ecs",
        "flask-jwt-extended[asymmetric_crypto]",
        "pyyaml",
    ],
)
