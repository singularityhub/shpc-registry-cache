#!/usr/bin/env python3

import argparse
import os
import shpc.utils
import shutil
import requests
import re
import glob


here = os.path.abspath(os.path.dirname(__file__))

def get_parser():
    parser = argparse.ArgumentParser(
        description="SHPC Registry Counts Generator",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--registry", help="Path to registry root.", default=here)
    return parser


def main():

    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # Show args to the user
    print("    registry: %s" % args.registry)

    counts = {}
    
    # Allow developer to provide tags in root
    for filename in shpc.utils.recursive_find(args.registry, ".json"):
        aliases = shpc.utils.read_json(filename)
        for alias, _ in aliases.items():
            if alias not in counts:
                counts[alias] = 0
            counts[alias] += 1

    shpc.utils.write_json(counts, "counts.json")
    
if __name__ == "__main__":
    main()
