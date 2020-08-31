#!/usr/bin/env python3
import re
from os import path

from setuptools import find_packages, setup

curpath = path.abspath(path.dirname(__file__))
with open(path.join(curpath, "README.md")) as f:
    long_description = f.read()


def read(*parts):
    with open(path.join(curpath, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='pysjtu',
    version=find_version("pysjtu", "__init__.py"),
    description='The Python iSJTU client for Humans.',
    author='LightQuantum',
    author_email='cy.n01@outlook.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={
        'pysjtu': ['ocr/*.onnx']
    },
    url='https://github.com/PhotonQuantum/pysjtu',
    classifiers=(
        'Operating System :: OS Independent',
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
        'httpx==0.11.1',
        'marshmallow',
        'lxml'
    ],
    extras_require={
        "ocr": ["onnxruntime", "numpy", "Pillow"]
    },
    tests_require=['pytest',
                   'pytest-cov',
                   'pytest-mock',
                   'respx==0.9.0',
                   'flask']
)
