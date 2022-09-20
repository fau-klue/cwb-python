[![Python package](https://github.com/fau-klue/cwb-python/actions/workflows/python-package.yml/badge.svg)](https://github.com/fau-klue/cwb-python/actions/workflows/python-package.yml)

Note that cwb-python is **not actively maintained**. The most recent
PyPI-version is [0.2.2](https://pypi.org/project/cwb-python/) from
June 20, 2017. The code is identical to the
[0.2.1-branch](https://github.com/fau-klue/cwb-python/tree/v0.2.1).

If you are starting a new project using Python and the Corpus
Workbench, **consider using
[cwb-ccc](https://github.com/ausgerechnet/cwb-ccc),** which provides
similar (and more) functionality.


# CWB Python

This is a Python wrapper to the low-level API of CQP which allows you
to access CWB corpora in the same way as Perl's CWB::CL.

Make sure installed CWB in the standard location (`/usr/local` tree).
If you installed CWB in a non-standard location, point the setup in
the right direction with e.g.

    export CWB_DIR=/usr/local/cwb-3.4.10

To install the module, use setup.py:

    sudo python setup.py install

# Cython Compilation

The module ships with the generated .c files, so you do not need
Cython for the installation.

If you want to re-generate the .c files, you need Cython:

    pip install Cython

You can then compile the Cython code to C via

    cython -2 cwb_python/CWB/CL.pyx
    
# C Compilation

You can compile the C code via

    pipenv run python setup.py build_ext --inplace
    
or just build (see above) or create a source distribution

    pipenv run python setup.py sdist

# Usage

To give you an idea how to use the library, see the following sample:

```python
from cwb.cl import Corpus

# open the corpus
corpus=Corpus('TUEPP')
# get sentences and words
sentences=corpus.attribute('s','s')
words=corpus.attribute('word','p')
postags=corpus.attribute('pos','p')
# retrieve offsets of the 1235th sentence (0-based)
s_1234=sentences[1234]

for w,p in zip(words[s_1234[0]:s_1234[1]+1],postags[s_1234[0]:s_1234[1]+1]):
    print "%s/%s"%(w,p)
```

# Tests

In order to test the CWB.CL module's correct installation
independently of any CQP corpora, you can do a

    python -m doctest tests/idlist.txt

which should terminate with no output when everything is well.
