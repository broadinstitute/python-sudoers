#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Install pysudoers."""

import io
import os
import sys

from setuptools import find_packages
from setuptools import setup
from setuptools.command.install import install

VERSION = "1.0.1"


def get_long_description():
    """Retrieve the long description from the README file."""
    # Use io.open to support encoding on Python 2 and 3
    fileh = io.open("README.md", "r", encoding="utf8")
    desc = fileh.read()
    fileh.close()

    return desc


# This was a great idea!! https://github.com/levlaz/circleci.py/blob/master/setup.py
class VerifyVersionCommand(install):
    """Verify that the git tag matches our version."""
    description = "verify that the git tag matches our version"

    def run(self):
        """Check the CIRCLE_TAG environment variable against the recorded version."""
        tag = os.getenv("CIRCLE_TAG")

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(tag, VERSION)
            sys.exit(info)


setup(
    name="pysudoers",
    version=VERSION,
    author="Andrew Teixeira",
    author_email="teixeira@broadinstitute.org",
    description="Python interface to the Linux sudoers file",
    include_package_data=True,
    keywords=["linux", "sudoers"],
    license="BSD",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests")),
    url="https://github.com/broadinstitute/python-sudoers",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=2.7, <4",
    setup_requires=["setuptools_scm"],
    cmdclass={"verify": VerifyVersionCommand},
)
