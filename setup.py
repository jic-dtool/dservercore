from setuptools import setup

setup(
    name="dtool-lookup-server",
    packages=["dtool_lookup_server"],
    include_package_data=True,
    package_data={"dtool_lookup_server": ["templates/*"]},
    entry_points={
        'flask.commands': [
            'register_user=dtool_lookup_server.cli:register_user',
            'register_base_uri=dtool_lookup_server.cli:add_base_uri',
            'give_search_permission=dtool_lookup_server.cli:give_search_permission',  # NOQA
            'give_register_permission=dtool_lookup_server.cli:give_register_permission',  # NOQA
            'generate_token=dtool_lookup_server.cli:generate_token',
            'index_base_uri=dtool_lookup_server.cli:index_base_uri',
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
