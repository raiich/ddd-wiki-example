#!/usr/bin/env python
from setuptools import setup

setup(
    name='mywiki-ddd-example',
    version='0.0.1',
    description='simple example of domain driven design',
    license='GNU General Public License v3.0',
    packages=[
        'mywiki'
    ],
    install_requires=[
        'mistune',
        'flask'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': ['mywiki=mywiki.__main__:main']
    },
)
