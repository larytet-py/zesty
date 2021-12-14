import os
import pytest
from typing import Dict, List

# return the positive sibling of a pair. For example,
# -7 4 -3 2 2 -8 -2 3 3 7 -2 3 -2 -> 7,3,2,2
# Try python3 -m pytest -v .


def test_main():
    input = [9, -11, 0, -7, 4, -3, 2, 2, -8, -2, 3, 3, 7, -2, 3, -2, -9, 11, 0]
    expected_output = [7, 3, 2, 2, 9, 11]

    negative_numbers, positive_numbers = {}, {}
    output: List[int] = []

    for val in input:
        if not val:
            continue
        _dict_sibling, _dict = positive_numbers, negative_numbers
        if val < 0:
            _dict_sibling, _dict = _dict, _dict_sibling
        val = abs(val)
        if _dict_sibling.get(val, 0):
            output.append(val)
            _dict_sibling[val] -= 1
        else:
            _dict[val] = _dict.get(val, 0) + 1

    output.sort()
    expected_output.sort()
    assert output == expected_output, f"actual {output}, expected {expected_output}"
