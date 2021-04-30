#!/usr/bin/env python3

import io
import os
from os import popen
from setuptools import find_packages
from distutils.core import setup, Extension


# Package meta-data
NAME = 'cwb-python'
DESCRIPTION = 'CQP and CL interfaces for Python'
URL = 'https://github.com/fau-klue/cwb-python/'
EMAIL = 'yversley@googlemail.com'
AUTHOR = 'Yannick Versley'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.3.0'

REQUIRED = [
]

here = os.path.abspath(os.path.dirname(__file__))

# for CWB >= 3.0
extra_libs = ['pcre', 'glib-2.0']

if 'CWB_DIR' in os.environ:
    cwb_dir = os.environ['CWB_DIR']
else:
    cqp_location = popen('which cqp').read().rstrip()
    cwb_dir = os.path.dirname(cqp_location)


# Import the README and use it as the long-description.
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# Register extension
USE_CYTHON = False              # use cython -2 cwb_python/CWB/CL.pyx instead
ext = '.pyx' if USE_CYTHON else '.c'

extensions = [
    Extension(name='cwb.cl',
              sources=['cwb/cl' + ext],
              library_dirs=[os.path.join(cwb_dir, 'include')],
              libraries=['cl'] + extra_libs)
]

if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions)

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "test_*"]),
    ext_modules=extensions,
    install_requires=REQUIRED,
    include_package_data=True,
    py_modules=['cqp'],
    entry_points={
        'console_scripts': [
            'cqp2conll = cwb.tools.cqp2conll:main',
            'cqp_bitext = cwb.tools.make_bitext:main',
            'cqp_vocab = cwb.tools.cqp2vocab:cqp2vocab_main'
        ]},
    package_dir={'cwb': 'cwb'}
)
