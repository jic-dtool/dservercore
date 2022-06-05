from setuptools import setup

url = ""
version = "0.1.0"
readme = open('README.rst').read()

setup(
    name="dtool-lookup-server-core",
    packages=["dtool_lookup_server_core"],
    description="Core component of dtool-lookup-server",
    long_description=readme,
#    package_data={"dtool_lookup_server_core": ["templates/*"]},
#    include_package_data=True,
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@gmail.com",
    version=version,
    url=url,
    entry_points={
    },
    install_requires=[
    ],
    download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)
