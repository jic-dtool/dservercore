from setuptools import setup
setup(
    name="core",
    packages=["core"],
    entry_points={
        "core.hook": [
            "echo=core:echo",
        ],
    },
)
