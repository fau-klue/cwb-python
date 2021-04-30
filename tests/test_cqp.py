#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from cwb.cqp import CQP


def test_cqp_with_no_cwb_binary():
    with pytest.raises(RuntimeError):
        CQP(binary=None)


def test_cqp_version():
    print()
    print("... you should see your CQP version below ...")
    CQP(print_version=True)
