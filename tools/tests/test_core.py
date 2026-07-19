"""Tests for cfdvv package."""

import os
import tempfile

import numpy as np
import pytest

from cfdvv.norms import l1_norm, l2_norm, linf_norm, relative_l2_norm, compute_norm
from cfdvv.readers import read_csv


class TestNorms:
    def test_l1_norm(self):
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([1.0, 2.0, 3.0])
        assert l1_norm(a, b) == 0.0

        a = np.array([1.0, 2.0, 3.0])
        b = np.array([2.0, 3.0, 4.0])
        assert l1_norm(a, b) == 1.0

    def test_l2_norm(self):
        a = np.array([0.0, 0.0])
        b = np.array([3.0, 4.0])
        assert l2_norm(a, b) == pytest.approx(3.5355339, rel=1e-6)

        a = np.array([1.0, 1.0])
        b = np.array([1.0, 1.0])
        assert l2_norm(a, b) == 0.0

    def test_linf_norm(self):
        a = np.array([1.0, 5.0, 3.0])
        b = np.array([2.0, 3.0, 3.0])
        assert linf_norm(a, b) == 2.0

    def test_relative_l2_norm(self):
        a = np.array([1.0, 2.0])
        b = np.array([2.0, 3.0])
        result = relative_l2_norm(a, b)
        assert result > 0

    def test_compute_norm(self):
        a = np.array([1.0, 2.0])
        b = np.array([3.0, 4.0])
        val, label = compute_norm(a, b, "L2")
        assert label == "L2"
        assert val > 0

    def test_unknown_norm(self):
        with pytest.raises(ValueError, match="Unknown norm"):
            compute_norm(np.array([1.0]), np.array([1.0]), "UNKNOWN")


class TestReaders:
    def test_read_csv_simple(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write("x,y,u,v\n")
            f.write("0,0,1.5,0.1\n")
            f.write("1,0,2.0,0.2\n")
            tmp = f.name

        try:
            data, cols = read_csv(tmp)
            assert len(cols) == 4
            assert cols[0].lower() == "x"
            assert cols[2].lower() == "u"
            assert data.shape == (2, 4)
            assert data[0, 2] == 1.5
        finally:
            os.unlink(tmp)

    def test_read_csv_no_header(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write("0.0, 0.5\n")
            f.write("1.0, 1.5\n")
            tmp = f.name

        try:
            data, cols = read_csv(tmp)
            assert data.shape == (2, 2)
            assert data[0, 0] == 0.0
        finally:
            os.unlink(tmp)

    def test_read_csv_with_header(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write("y, u\n")
            f.write("0.0, 0.5\n")
            f.write("0.5, 1.0\n")
            f.write("1.0, 1.5\n")
            tmp = f.name

        try:
            data, cols = read_csv(tmp)
            assert cols[0].lower() == "y"
            assert cols[1].lower() == "u"
            assert data.shape == (3, 2)
            assert data[2, 1] == 1.5
        finally:
            os.unlink(tmp)
