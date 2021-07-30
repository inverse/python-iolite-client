import os

from setuptools import setup


def read_version(package):
    with open(os.path.join(package, "__init__.py"), "r") as fd:
        for line in fd:
            if line.startswith("__version__ = "):
                return line.split()[-1].strip().strip("'")


VERSION = read_version("iolite")

setup(
    description="API client for interacting with IOLite's remote API",
    author="Malachi Soord",
    author_email="me@malachisoord.com",
    url="https://github.com/inverse/python-iolite-client",
    version=VERSION,
    install_requires=["requests", "websockets", "environs"],
    test_requires=["pylama", "pytest"],
    name="iolite",
    dependency_links=[],
)
