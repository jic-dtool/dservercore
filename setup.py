from setuptools import setup

setup(
    name="dtool-lookup-server",
    packages=["dtool_lookup_server"],
    include_package_data=True,
    package_data={"dtool_lookup_server": ["templates/*"]},
    entry_points={
        'flask.commands': [
            'register_user=dtool_lookup_server.cli:register_user'
        ],
    },
    install_requires=[
        "cryptography",
        "flask",
        "flask-sqlalchemy",
        "flask-migrate",
        "flask-pymongo",
        "dtoolcore",
        "dtool_irods",
        "dtool_s3",
        "pyjwt",
        "pyyaml",
    ],
)
