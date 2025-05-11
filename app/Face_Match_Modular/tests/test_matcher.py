import numpy as np
import pytest

from Face_Match_Modular import find_best_match

@pytest.mark.parametrize("known, query, threshold, expected", [
    # perfect 1-D match
    (["A"], [[0.0]], [0.0], 0.1, (True, "A", 0.0)),
    # slightly below threshold
    (["A"], [[0.0]], [0.05], 0.1, (True, "A", pytest.approx(0.05))),
    # exactly at threshold → no match (because < threshold)
    (["A"], [[0.0]], [0.1], 0.1, (False, None, pytest.approx(0.1))),
    # slightly above threshold → no match
    (["A"], [[0.0]], [0.15], 0.1, (False, None, pytest.approx(0.15))),
    # two suspects, closer to B
    (["A","B"], [[0,0,0],[1,1,1]], [0.9,0.9,0.9], 2.0, (True, "B", pytest.approx(np.linalg.norm([1,1,1] - [0.9,0.9,0.9])))),
])
def test_find_best_match_various(known, query, threshold, expected):
    names = known
    known_encs = np.array(query, dtype=float)
    query_enc = np.array(query[-1], dtype=float)  # last vector
    matched, name, dist = find_best_match(names, known_encs, query_enc, threshold)
    exp_matched, exp_name, exp_dist = expected
    assert matched is exp_matched
    assert name == exp_name
    assert dist == exp_dist

def test_empty_known():
    # no suspects on file
    matched, name, dist = find_best_match([], np.array([]), np.array([0.1]), 0.2)
    assert matched is False
    assert name is None
    assert dist is None

def test_multi_dimensional():
    # 5-D vectors
    names = ["X","Y"]
    known = np.array([
        [1,2,3,4,5],
        [5,4,3,2,1]
    ], dtype=float)
    # query exactly equal to second
    query = np.array([5,4,3,2,1], dtype=float)
    matched, name, dist = find_best_match(names, known, query, threshold=0.01)
    assert matched is True
    assert name == "Y"
    assert dist == pytest.approx(0.0)
