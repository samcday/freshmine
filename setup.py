#!/usr/bin/env python

from setuptools import setup

setup(
    name='freshmine',
    version='1.0',
    author='Sam Day',
    author_email='me@samcday.com.au',
    install_requires=[
        "pytz",
        "refreshbooks",
        "pyredmine",
        "python-dateutil",
        "requests"
    ]
)
