from py_ecog_utils import line_length
import numpy as np
import pytest
from pytest import approx

matrix_vec = np.tile(np.arange(1,11),(2,1)).T
single_vec = np.array([[[1,2,3,4,5,6,7,8,9,10]]])

diffs_correct = np.repeat(2,7)

correct_single = np.concatenate((diffs_correct, np.array([np.nan, np.nan, np.nan])),axis=0).T
correct_matrix= np.tile(correct_single, (2, 1)).T

def test_typical():
    assert line_length.line_length_transform(matrix_vec, sfx=1, llw=3) == approx(correct_matrix,nan_ok=True)
    assert line_length.line_length_transform(single_vec, sfx=1, llw=3) == approx(correct_single,nan_ok=True)