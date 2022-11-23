#!/usr/bin/env python3

import argparse
import os
import shpc.utils
import requests
from bs4 import BeautifulSoup


# .github/scripts
here = os.path.abspath(os.path.dirname(__file__))
root = os.path.dirname(os.path.dirname(here))


def get_parser():
    parser = argparse.ArgumentParser(
        description="SHPC BioContainer Adder",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "filename", help="Path to filename to write container listing to."
    )
    return parser


def main():

    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # Show args to the user
    print("filename: %s" % args.filename)

    response = requests.get("https://depot.galaxyproject.org/singularity/")
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")

    images = set()

    # Use the latest for each unique
    for link in links:
        if ":" not in link.text:
            continue
        image, tag = link.text.split(":", 1)
        images.add(image)

    print("Found %s BioContainers images" % len(images))

    # Write skips back to file for faster parsing
    text = "\n".join(sorted(list(images)))
    shpc.utils.write_json(text, args.filename)


if __name__ == "__main__":
    main()
