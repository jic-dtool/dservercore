from setuptools import setup

url = "https://github.com/livMatS/dserver"
version = "0.18.0"
readme = open('README.rst').read()

setup(
    name="dserver",
    packages=["dserver"],
    description="Web API to register/lookup/search for dtool dataset metadata",
    long_description=readme,
    long_description_content_type="text/x-rst",
    package_data={"dserver": ["templates/*"]},
    include_package_data=True,
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@gmail.com",
    version=version,
    url=url,
    entry_points={
        'flask.commands': [
            'base_uri=dserver.cli:base_uri_cli',
            'user=dserver.cli:user_cli',
            'config=dserver.cli:config_cli',
            'dataset=dserver.cli:dataset_cli',
        ],
    },
    install_requires=[
        "flask<3",
        "pymongo",
        "alembic",
        "flask-sqlalchemy",
        "flask-migrate",
        "flask-pymongo",
        "flask-marshmallow",
        "flask-smorest",
        "marshmallow-sqlalchemy",
        "flask-cors",
        "dtoolcore>=3.18.0",
        "flask-jwt-extended[asymmetric_crypto]>=4.0",
        "pyyaml",
    ],
    download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)
