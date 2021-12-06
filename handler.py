"""
Usage:
pip3 install -r requirements.txt
AWS_ACCESS_KEY_ID="key is here" AWS_SECRET_ACCESS_KEY="secret key" AWS_SESSION_TOKEN="session key" python3 ./handler.py


You can also install ket keys permanently 
See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
"""

import sys
from datetime import date, datetime
import easyargs
from typing import Set, List, Dict, Tuple
import re
import logging
import json
import boto3


# Helper to translate AWS datatime to ISO format
def datetime_converter(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type {} is not serializable".format(type(obj)))


def validate_region(region: str):
    """
    Regex match fot stuff like 'eu-west-1'
    """
    m = re.match(r"^[a-z]{2}-[a-z]+-[0-9]+$", region)
    return m is not None


def load_regions(regions_filename) -> Set[str]:
    regions: Set[str] = set()
    with open(regions_filename, "rt") as f:
        for l in f:
            regions_in_line = l.split(",")
            for region in regions_in_line:
                region = region.strip()
                if not validate_region(region):
                    logging.error(
                        f"Region '{region}' in {regions_filename} is not valid"
                    )
                    continue
                regions.add(region)

    return regions


def dump_regions(ec2_instances: Dict[str, List[str]]):
    serializable_instances = {}
    for region, instances in ec2_instances.items():
        # Object of type ec2.Instance is not JSON serializable
        serializable_instances = [
            {"instance_id": i.instance_id, "launch_time": i.launch_time}
            for i in instances
        ]
        s = json.dumps(serializable_instances)
        json_filename = f"{region}.json"
        with open(json_filename, "wt") as f:
            f.write(s)


def load_ec2_instances(region: str) -> Tuple[List[str], bool]:
    """
    Based on https://stackoverflow.com/questions/63571591
    """

    try:
        ec2 = boto3.resource("ec2", region_name=region)
    except:
        logging.exception(f"Failed to get EC2 instaces from AWS")
        return {}, False

    running_instances = ec2.instances.filter(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )

    # 'ec2.instancesCollection' object has no attribute 'sort'
    running_instances = [r for r in running_instances]
    running_instances.sort(
        key=lambda x: datetime_converter(x.launch_time), reverse=True
    )

    return running_instances, True


@easyargs
def main(regions_filename="regions.txt"):
    logging.basicConfig(level=logging.DEBUG)
    regions = load_regions(regions_filename)
    if not regions:
        logging.error(f"No valid regions in {regions_filename}")
        return -1

    logging.info(f"Loaded regions {regions}")

    ec2_instances: Dict[str, List[str]] = {}
    for region in regions:
        instances, ok = load_ec2_instances(region)
        if not ok:
            continue
        ec2_instances[region] = instances
    dump_regions(ec2_instances)

    return 0


if __name__ == "__main__":
    sys.exit(main())
