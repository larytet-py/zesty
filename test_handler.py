import pytest

from typing import List
from collections import namedtuple
import handler


def test_region_to_filename():
    assert handler.region_to_filename("test") == "test.json"


validate_region_testdata = [
    ("eu-west-1", True),
    ("us-east-1", True),
    ("eu-west-1", True),
    ("ap-southeast-1", True),
    ("ap-southeast-11", True),
    ("a", False),
    ("eu-west-1 ", False),
    ("eu1-west-1", False),
    ("e-west-12", False),
]


@pytest.mark.parametrize("s, expected", validate_region_testdata)
def test_validate_region(s, expected):
    assert handler.validate_region(s) == expected


EC2Instance = namedtuple(
    "EC2Instance", ["instance_id", "launch_time", "public_ip_address"]
)


class EC2Instances:
    def __init__(self, instances: List[EC2Instance]):
        self.instances = instances

    def filter(self):
        return self.instances


class BOTO3Mock:
    def __init__(self):
        pass

    def resource(self, region_name):
        return EC2Instances([EC2Instance("1", datetime.now(), "1.1.1.1")])


def test_load_ec2_instances():
    handler.load_ec2_instances(BOTO3Mock(), "eu-west-1")
