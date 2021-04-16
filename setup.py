#!/usr/bin/env python


import io
import os
from setuptools import find_packages
from distutils.core import setup
from distutils.extension import Extension


# Package meta-data.
NAME = 'cwb-python'
DESCRIPTION = 'CQP and CL interfaces for Python'
URL = 'https://github.com/fau-klue/cwb-python/'
EMAIL = 'yversley@googlemail.com'
AUTHOR = 'Yannick Versley / Jorg Asmussen'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.2.3'

REQUIRED = [
]

here = os.path.abspath(os.path.dirname(__file__))

# for CWB 2.2
# extra_libs = []
# for CWB >= 3.0
extra_libs = ['pcre', 'glib-2.0']

if 'CWB_DIR' in os.environ:
    cqp_dir = os.environ['CWB_DIR']
else:
    # TODO: Make dynamic if possible
    cqp_location = '/usr/local/bin/cqp'
    cqp_dir = os.path.dirname(cqp_location)


# Import the README and use it as the long-description.
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# Import Cython if available
try:
    from Cython.Build import cythonize
    CYTHON_INSTALLED = True
    # Cython Code
    extensions = [Extension('cwb_python.CWB.CL', ['cwb_python/CWB/CL.pyx'],
                            library_dirs=[os.path.join(cqp_dir, 'lib')],
                            libraries=['cl'] + extra_libs)]

except ImportError:
    cythonize = lambda x, *args, **kwargs: x  # dummy func
    CYTHON_INSTALLED = False
    # Already compiled Cython
    extensions = [Extension('cwb_python.CWB.CL', ['cwb_python/CWB/CL.c'],
                            library_dirs=[os.path.join(cqp_dir, 'lib')],
                            libraries=['cl'] + extra_libs)]


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
    ext_modules=cythonize(extensions),
    install_requires=REQUIRED,
    include_package_data=True,
    py_modules=['CQP'],
    entry_points={
        'console_scripts': [
            'cqp2conll = CWB.tools.cqp2conll:main',
            'cqp_bitext = CWB.tools.make_bitext:main',
            'cqp_vocab = CWB.tools.cqp2vocab:cqp2vocab_main'
        ]},
    package_dir={'cwb-python': 'cwb_python'}
)
