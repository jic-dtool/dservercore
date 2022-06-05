from setuptools import setup

url = ""
version = "0.1.0"
readme = open('README.rst').read()

setup(
    name="dtool-lookup-server-auth",
    packages=["dtool_lookup_server_auth"],
    description="Authentication component of dtool-lookup-server",
    long_description=readme,
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@gmail.com",
    version=version,
    url=url,
    entry_points={
        "dtool_lookup_server.auth": [
                "dls_auth=dtool_lookup_server_auth:Auth",
            ],
    },
    install_requires=[
    ],
    download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)
