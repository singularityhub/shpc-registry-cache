#!/usr/bin/env python3

import argparse
import os
from container_guts.main import ManifestGenerator
import shpc.utils
import shutil
import requests
import glob
from bs4 import BeautifulSoup

import pipelib.steps as step
import pipelib.pipeline as pipeline


# .github/scripts
here = os.path.abspath(os.path.dirname(__file__))
root = os.path.dirname(os.path.dirname(here))


def get_parser():
    parser = argparse.ArgumentParser(
        description="SHPC BioContainer Adder",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--cache", help="Path to cache root.", default=root)
    return parser


# A pipeline to process docker tags
steps = (
    # Scrub commits from version string
    step.filters.CleanCommit(),
    # Parse versions, return sorted ascending, and taking version major.minor.patch into account
    step.container.ContainerTagSort(),
)
p = pipeline.Pipeline(steps)


def has_cache_entry(image, registry):
    """
    Determine if there is a cache entry based on presence of json files.
    """
    # If we already have the registry entry (for any tag) skip
    letter = image[0].lower()
    json_dirs = glob.glob(
        "%s*.json" % os.path.join(registry, "quay.io", "biocontainers", letter, image)
    )
    return len(json_dirs) > 0


def get_tags(links, registry):
    uris = {}

    # Use the latest for each unique
    for link in links:
        if ":" not in link.text:
            continue
        image, tag = link.text.split(":", 1)

        if has_cache_entry(image, registry) or image in uris:
            continue

        print(f"Retrieving tags for {image}")
        tags = requests.get(f"https://crane.ggcr.dev/ls/quay.io/biocontainers/{image}")
        uris[image] = [x for x in tags.text.split("\n") if x]
    return uris


def main():

    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # Show args to the user
    print("    cache: %s" % args.cache)

    response = requests.get("https://depot.galaxyproject.org/singularity/")
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")

    # Allow developer to provide tags in root
    uris = get_tags(links, args.cache)

    skips_file = os.path.join(root, "skips.json")
    skips = set()
    if os.path.exists(skips_file):
        skips = set(shpc.utils.read_json(skips_file))

    # Ensure our alias cache exists
    if not os.path.exists(args.cache):
        shpc.utils.mkdir_p(args.cache)

    # For each uri, get latest version of tags not an error
    for uri, tags in uris.items():

        if uri in skips:
            continue

        if "UNAUTHORIZED" in tags[0]:
            skips.add(uri)
            continue

        if has_cache_entry(uri, args.cache):
            continue

        # The updated and transformed items
        ordered = p.run(list(tags), unwrap=False)
        if not ordered:
            skips.add(uri)
            continue

        tag = ordered[0]._original
        container = f"quay.io/biocontainers/{uri}:{tag}"
        print(f"Looking up aliases for {container}")
        try:
            cache_aliases(container, args.cache, uri, tag)
        except:
            skips.add(uri)
            for path in glob.glob("/tmp/guts*"):
                shutil.rmtree(path)

    # Write skips back to file for faster parsing
    shpc.utils.write_json(list(skips), skips_file)


def include_path(path):
    """
    Filter out binaries that are in system bins.
    """
    return "sbin" not in path and "/usr/bin" not in path and not path.startswith("/bin")


def cache_aliases(container, cache, uri, tag):
    """
    Keep a cache of aliases to use later
    """
    letter = uri[0].lower()
    filename = os.path.join(
        cache, "quay.io", "biocontainers", letter, "%s:%s.json" % (uri, tag)
    )
    prefix = os.path.join(cache, "quay.io", "biocontainers", letter, "%s*" % uri)

    # Any glob of the container
    if os.path.exists(filename) or glob.glob(prefix):
        return shpc.utils.read_json(filename)

    # Generate guts
    gen = ManifestGenerator()
    manifests = gen.diff(container)

    # Assemble aliases
    aliases = {}
    for path in list(manifests.values())[0]["diff"]["unique_paths"]:
        name = os.path.basename(path)
        if not include_path(path):
            continue

        if name in aliases:
            print(f"Warning, duplicate alias {name}")
        print(path)
        aliases[name] = path

    parent = os.path.dirname(filename)
    shpc.utils.mkdir_p(parent)
    print(f"Writing {filename} with aliases")
    shpc.utils.write_json(aliases, filename)
    return aliases


if __name__ == "__main__":
    main()
