from setuptools import setup

url = ""
version = "0.1.0"
readme = open('README.rst').read()

setup(
    name="dtool-lookup-server-search",
    packages=["dtool_lookup_server_search"],
    description="Search component of dtool-lookup-server",
    long_description=readme,
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@gmail.com",
    version=version,
    url=url,
    entry_points={
        "dtool_lookup_server.search": [
                "dls_search=dtool_lookup_server_search:Search",
            ],
    },
    install_requires=[
    ],
    download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)
