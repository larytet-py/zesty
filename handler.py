"""
Usage:

pip3 install -r requirements.txt
AWS_ACCESS_KEY_ID="key is here" \
AWS_SECRET_ACCESS_KEY="secret key" \
AWS_SESSION_TOKEN="session key" \
python3 ./handler.py

AWS_ACCESS_KEY_ID="key is here" \
AWS_SECRET_ACCESS_KEY="secret key" \
AWS_SESSION_TOKEN="session key" \
python3 ./handler.py --get_instances="eu-west-1"

Typical output 
[
   {
      "instance_id":"i-0c09c8a02e1342060",
      "launch_time":"2021-10-27 12:14:19+00:00"
   },
   {
      "instance_id":"i-0684e37a479b7afee",
      "launch_time":"2021-10-31 10:27:23+00:00"
   },
   {
      "instance_id":"i-03e9c588257859ac9",
      "launch_time":"2021-11-30 11:26:00+00:00"
   },
   {
      "instance_id":"i-0093b4a49156267b8",
      "launch_time":"2021-11-30 11:26:01+00:00"
   }
]

You can also install ket keys permanently 
See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html


Development

black .
python3 -m pytest -v .
"""

import os
import sys
from datetime import date, datetime
import easyargs
from typing import Set, List, Dict, Tuple
import re
import logging
import json
import boto3, botocore


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

    # TODO check if the region exists
    # https://stackoverflow.com/questions/38451032
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


def region_to_filename(region: str) -> str:
    return f"{region}.json"


def rm_json_files():
    for f in os.listdir("./"):
        region = os.path.basename(f).split(".")[0]
        if validate_region(region):
            os.remove(f)


def dump_regions(ec2_instances: Dict[str, List[str]]):
    # remove JSON files first
    rm_json_files()

    serializable_instances = {}
    for region, instances in ec2_instances.items():
        # Object of type ec2.Instance is not JSON serializable
        serializable_instances = [
            {"instance_id": i.instance_id, "launch_time": str(i.launch_time)}
            for i in instances
        ]
        s = json.dumps(serializable_instances, sort_keys=False, indent=4)
        json_filename = region_to_filename(region)
        # TODO handle exception in case there is a folder with the same name
        # or write access problems
        with open(json_filename, "wt") as f:
            f.write(s)


def load_ec2_instances(region: str) -> Tuple[List[str], bool]:
    """
    Based on https://stackoverflow.com/questions/63571591
    """

    try:
        ec2 = boto3.resource("ec2", region_name=region)
    except:
        # TODO some exceptgions crash the code. Why?
        # for example botocore.exceptions.EndpointConnectionError
        # Could not connect to the endpoint URL: "https://ec2.ez-southeast-1.amazonaws.com/"
        logging.exception(f"Failed to get EC2 instaces from AWS")
        return [], False

    running_instances = ec2.instances.filter(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )

    # 'ec2.instancesCollection' object has no attribute 'sort'
    running_instances = [r for r in running_instances]
    running_instances.sort(
        key=lambda x: datetime_converter(x.launch_time), reverse=False
    )

    return running_instances, True


def get_instances_for_region(region: str) -> str:
    data = ""
    json_filename = region_to_filename(region)
    if not os.path.exists(json_filename):
        logging.error(f"I don;t have filename {json_filename} region {region}")
        return data

    with open(json_filename) as f:
        data = f.read()

    return data


@easyargs
def main(regions_filename="regions.txt", get_instances=""):
    # See https://stackoverflow.com/questions/1661275
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    logging.basicConfig(level=logging.DEBUG)

    if get_instances:
        s = get_instances_for_region(get_instances)
        logging.info(f"{s}")
        return

    regions = load_regions(regions_filename)
    if not regions:
        logging.error(f"No valid regions in {regions_filename}")
        return -1

    logging.info(f"Loaded regions {regions}")

    ec2_instances: Dict[str, List[str]] = {}
    for region in regions:
        instances, ok = load_ec2_instances(region)
        if not ok:
            logging.error(f"Failed to get EC2 instances for {region}")
            continue
        if not instances:
            logging.info(f"No instances in {region}")
            continue

        ec2_instances[region] = instances
    dump_regions(ec2_instances)

    return 0


if __name__ == "__main__":
    sys.exit(main())
