import os
import pytest
from typing import Dict, List

# print the numbers having a matching numnber with an opposite sign
# -7 4 -3 2 2 -8 -2 3 3 7 -2 3 -2 -> 7,3,2,2
# Try python3 -m pytest -v .


# Alternative solution:
#  * Sort the original array
#  * Move in two directions from left to right and from right to left
#  * Match pairs, skip numbers without matches

def test_main():
    input = [9, -11, 0, -7, 4, -3, 2, 2, -8, -2, 3, 3, 7, -2, 3, -2, -9, 11, 0]
    expected_output = [7, 3, 2, 2, 9, 11]

    counters = {}
    output: List[int] = []

    for val in input:
        if not val:
            continue

        if counters.get(-val, 0):
            counters[-val] -= 1
            output.append(abs(val))
            continue

        counters[val] = counters.get(val, 0) + 1


    output.sort()
    expected_output.sort()
    assert output == expected_output, f"actual {output}, expected {expected_output}"
