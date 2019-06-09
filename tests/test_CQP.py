import pytest

from cwb_python.CQP import CQP


def test_CQP_init():
    with pytest.raises(RuntimeError):
        cqp = CQP()
