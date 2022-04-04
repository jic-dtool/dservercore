from setuptools import setup
setup(
    name="plugin",
    packages=["plugin"],
    install_requires=["core"],
    entry_points={
        "core.hook": [
            "echo=plugin:echo",
        ],
    },
)
