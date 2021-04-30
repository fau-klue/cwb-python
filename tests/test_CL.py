import pytest

from cwb_python.CWB.CL import Corpus


def test_corpus_with_no_corpus():
    with pytest.raises(KeyError):
        corpus = Corpus('foobar')
