import os
import pytest
from typing import Dict, List

# return the positive sibling of a pair. For example,
# -7 4 -3 2 2 -8 -2 3 3 7 -2 3 -2 -> 7,3,2,2


def update_dict(d: Dict[int, int], val: int):
    counter = d.get(val, 0)
    d[val] = counter + 1


def test_main():
    input = [-7, 4, -3, 2, 2, -8, -2, 3, 3, 7, -2, 3, -2, -9, 0]
    expected_output = [7, 3, 2, 2]

    negative_numbers, positive_numbers = {}, {}
    output: List[int] = []

    for val in input:
        if val > 0:
            if negative_numbers.get(-val, 0):
                output.append(val)
                negative_numbers[-val] -= 1
            else:``
                update_dict(positive_numbers, val)

        if val < 0:
            if positive_numbers.get(-val, 0):
                output.append(-val)
                positive_numbers[-val] -= 1
            else:
                update_dict(negative_numbers, val)

    assert (
        output.sort() == expected_output.sort()
    ), f"actual {output}, expected {expected_output}"
