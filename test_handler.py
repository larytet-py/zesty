import pytest

import handler

def test_region_to_filename():
    assert handler.region_to_filename("test") == "test.json"
