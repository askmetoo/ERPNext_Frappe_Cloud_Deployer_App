# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in deployer/__init__.py
from deployer import __version__ as version

setup(
	name='deployer',
	version=version,
	description='Deploys all the new fields, doctypes, properties, print formats, workflows etc..',
	author='Promantia',
	author_email='paul.clinton@promantia.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
