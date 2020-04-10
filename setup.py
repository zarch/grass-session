#!/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages

os.chdir(os.path.dirname(sys.argv[0]) or ".")

setup(
    name="grass-session",
    version="0.3",
    description="GRASS GIS session utilities",
    long_description=open("README.rst", "rt").read(),
    url="https://github.com/zarch/grass-session",
    author="Pietro Zambelli",
    author_email="peter.zamb@gmail.com",
    # list of valid classifiers
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    packages=find_packages(),
)
