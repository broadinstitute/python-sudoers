#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Install pysudoers."""

import io
import setuptools


def get_long_description():
    """Retrieve the long description from the README file."""
    # Use io.open to support encoding on Python 2 and 3
    fileh = io.open("README.md", "r", encoding="utf8")
    desc = fileh.read()
    fileh.close()

    return desc


setuptools.setup(
    name="pysudoers",
    version="0.1.0",
    author="Andrew Teixeira",
    author_email="teixeira@broadinstitute.org",
    description="Python interface to the Linux sudoers file",
    include_package_data=True,
    keywords=["linux", "sudoers"],
    license="BSD",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=("tests")),
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
)
