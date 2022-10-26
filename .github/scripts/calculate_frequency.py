#!/usr/bin/env python3

import collections
import argparse
import os
import json
import re

here = os.path.abspath(os.path.dirname(__file__))
root = os.path.dirname(os.path.dirname(here))


def recursive_find(base, pattern=None):
    """
    Find filenames that match a particular pattern, and yield them.
    """
    # We can identify modules by finding module.lua
    for root, folders, files in os.walk(base):
        for file in files:
            fullpath = os.path.abspath(os.path.join(root, file))

            if pattern and not re.search(pattern, fullpath):
                continue
            yield fullpath


def write_json(json_obj, filename, mode="w"):
    """
    Write json to a filename
    """
    with open(filename, mode) as filey:
        filey.writelines(print_json(json_obj))
    return filename


def print_json(json_obj):
    """
    Print json pretty
    """
    return json.dumps(json_obj, indent=4, separators=(",", ": "))


def read_file(filename, mode="r"):
    """
    Read a file.
    """
    with open(filename, mode) as filey:
        content = filey.read()
    return content


def read_json(filename, mode="r"):
    """
    Read a json file to a dictionary.
    """
    return json.loads(read_file(filename))


def get_parser():
    parser = argparse.ArgumentParser(
        description="SHPC Registry Counts Generator",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--registry", help="Path to registry root.", default=root)
    return parser


def main():

    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # Show args to the user
    print("    registry: %s" % args.registry)

    counts = {}

    # Allow developer to provide tags in root
    for filename in recursive_find(os.path.join(args.registry, "quay.io"), ".json"):
        aliases = read_json(filename)
        for alias in aliases:
            if alias not in counts:
                counts[alias] = 0
            counts[alias] += 1

    counts = collections.OrderedDict(sorted(counts.items()))
    write_json(counts, os.path.join(root, "counts.json"))


if __name__ == "__main__":
    main()
