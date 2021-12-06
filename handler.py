"""
Usage:
pip3 install -r requirements.txt
AWS_ACCESS_KEY_ID="key is here" AWS_SECRET_ACCESS_KEY="secret key" python3 ./handler.py


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
    regions: Set[str] = {}
    with open(regions_filename, "r") as f:
        for l in f.readline():
            regions_in_line = l.split(",")
            for region in regions_in_line:
                region = region.strip()
                if not validate_region(l):
                    logging.error(f"Region {l} in {regions_filename} is not valid")
                    continue
                regions.add(region)

    return regions


def dump_regions(ec2_instances: Dict[str, List[str]]):
    for region, instances in ec2_instances.items():
        s = json.dumps(instances)
        json_filename = f"{region}.json"
        with open(json_filename, "w") as f:
            f.write(s)


def load_ec2_instances(region: str) -> Tuple[List[str], bool]:
    """
    Based on https://stackoverflow.com/questions/63571591
    """
    ec2 = boto3.resource("ec2", region_name=region)
    running_instances = ec2.instances.filter(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )
    logging.error(running_instances)

    # running_instances.sort(key=lambda x: x.launch_time, reverse=True)

    return ([], False)


@easyargs
def main(regions_filename="regions.txt"):
    logging.basicConfig(level=logging.DEBUG)
    regions = load_regions(regions_filename)
    if not regions:
        logging.error(f"No valid regions in {regions_filename}")
        return -1

    ec2_instances: Dict[str, List[str]] = {}
    for region in regions:
        instances, err = load_ec2_instances(regions)
        if err:
            continue
        ec2_instances[region] = instances
    dump_regions(ec2_instances)

    return 0


if __name__ == "__main__":
    sys.exit(main())
