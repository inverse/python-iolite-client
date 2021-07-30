from setuptools import setup

from iolite import __version__

setup(
    description="API client for interacting with IOLite's remote API",
    author="Malachi Soord",
    author_email="me@malachisoord.com",
    url="https://github.com/inverse/python-iolite-client",
    version=__version__,
    install_requires=["requests", "websockets", "environs"],
    test_requires=["pylama", "pytest"],
    name="iolite",
    dependency_links=[],
)
