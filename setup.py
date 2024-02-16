import os
from setuptools import setup
from setuptools_scm import get_version
version = get_version(root='.', relative_to=__file__)


def local_scheme(version):
    """Skip the local version (eg. +xyz of 0.6.1.dev4+gdf99fe2)
    to be able to upload to Test PyPI"""
    return ""

url = "https://github.com/livMatS/dserver"
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
    use_scm_version={
        "local_scheme": local_scheme,
        "root": '.',
        "relative_to": __file__,
        "write_to": os.path.join(
            "dserver", "version.py"),
    },
    url=url,
    entry_points={
        'flask.commands': [
            'base_uri=dserver.cli:base_uri_cli',
            'user=dserver.cli:user_cli',
            'config=dserver.cli:config_cli',
            'dataset=dserver.cli:dataset_cli',
        ],
    },
    setup_requires=['setuptools_scm'],
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
