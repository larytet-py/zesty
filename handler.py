from datetime import date, datetime
import easyargs
from typing import Set, List
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
    m = re.match(r"^[a-z]{2}-[a-z]+-[0-9]+$")
    return m is not None


def load_regions(regions_filename) -> Set[str]:
    regions: Set[str] = {}
    with open(regions_filename, "r") as f:
        for l in f.readline():
            if not validate_region(l):
                logging.error(f"Region {l} in {regions_filename} is not valid")
                continue
            regions.add(l)

    return regions


def dump_regions(ec2_instances: Dict[str, List[str]]):
    for region, instances in ec2_instances.items():
        s = json.dumps(instances)
        json_filename = f"{region}.json"
        with open(json_filename, "w") as f:
            f.write(s)


def load_ec2_instances(regions: Set[str]) -> List[str]:
    pass


@easyargs
def main(regions_filename="regions.txt"):
    logging.basicConfig(level=logging.DEBUG)
    regions = load_regions(regions_filename)
    if not regions:
        logging.error(f"No valid regions in {regions_filename}")
        return -1

    ec2_instances: Dict[str, List[str]] = {}
    for region in regions:
        ec2_instances[region], err = load_ec2_instances(regions)
    dump_regions(ec2_instances)

    return 0


if __name__ == "__main__":
    sys.exit(main())
