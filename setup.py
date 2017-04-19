#!/usr/bin/env python

from setuptools import setup

readme = open('README.md').read()
requirements = [l.strip() for l in open('requirements.txt').readlines()]

setup(
    name='copycat',
    version='0.0.1',
    packages=['copycat'],
    install_requires=[l.strip() for l in open('requirements.txt').readlines()],
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
