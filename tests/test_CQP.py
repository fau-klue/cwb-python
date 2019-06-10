import pytest

from cwb_python.CQP import CQP


def test_CQP_with_no_cwb_binary():
    with pytest.raises(RuntimeError):
        cqp = CQP()
