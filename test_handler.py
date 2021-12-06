import pytest

import handler


def test_region_to_filename():
    assert handler.region_to_filename("test") == "test.json"


validate_region_testdata = [
    ("eu-west-1", True),
    ("ap-southeast-11", True),
    ("a", False),
    ("eu-west-1 ", False),
    ("eu1-west-1", False),
    ("e-west-12", False),
]


@pytest.mark.parametrize("s, expected", validate_region_testdata)
def test_validate_region(s, expected):
    assert handler.validate_region(s) == expected
