#!/usr/bin/env python3

from setuptools import setup

import pysjtu

setup(
    name='pysjtu',
    version=pysjtu.__version__,
    description='The Python iSJTU client for Humans.',
    author='LightQuantum',
    author_email='cy.n01@outlook.com',
    packages=[
        'pysjtu',
    ],
    package_data={
        '': ['*.onnx']
    },
    url='https://github.com/PhotonQuantum/pysjtu',
    classifiers=(
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ),
    install_requires=[
        'httpx~=0.11.0',
        'marshmallow',
        'numpy',
        'Pillow>=7.0.0',
        'onnxruntime'
    ],
    tests_require=['pytest',
                   'pytest-cov',
                   'pytest-mock']
)
