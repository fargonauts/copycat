#!/usr/bin/env python
"""Self-explanatory."""
from setuptools import setup

setup(
    name='copycat',
    version='0.0.1',
    packages=['copycat'],
    install_requires=[
        # pip requirements go here; at the moment there are none
    ],
    package_data={'': ['LICENSE']},

    # metadata for upload to PyPI
    author="The Fluid Analogies Research Group, J Alan Brogan, and Arthur O'Dwyer",
    author_email='arthur.j.odwyer@gmail.com',
    description="Python implementation of Douglas Hofstadter's Copycat.",
    license='MIT license',
    long_description=open('README.md').read(),
    keywords='ai analogy copycat farg fargitecture hofstadter slipnet',
    url='https://github.com/Quuxplusone/co.py.cat',
)
