import pytest

from cwb.cl import Corpus


def test_corpus_with_no_corpus():
    with pytest.raises(KeyError):
        Corpus('foobar')
