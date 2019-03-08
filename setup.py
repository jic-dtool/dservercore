from setuptools import setup

setup(
    name='dtool-lookup-server',
    packages=['dtool_lookup_server'],
    include_package_data=True,
    install_requires=[
        'flask',
        'pymongo',
        'dtoolcore',
        'dtool_irods',
        'dtool_s3',
        'pyyaml',
    ],
)
