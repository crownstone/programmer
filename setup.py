#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='Programmer',
    version='0.0.1',
    packages=find_packages(exclude=["examples", "experiment", "tests", "techDocs"]),
    install_requires=[
        'RPi.GPIO',
        'BluenetLib==0.6.1'
    ],
    dependency_links=[
        'http://github.com/crownstone/bluenet-python-Programmer/tarball/master#egg=BluenetLib-0.6.1'
    ]
)
