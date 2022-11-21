# Shpc Registry Cache

This is a static cache of container executables discovered on the path. The cache is
updated once a week (Wednesday), and we store namespaced (based on OCI or Docker registry)
identifiers from the repository root here. Since we primarily cache the set of BioContainers,
that means the main set is under [quay.io](quay.io). These counts are useful for research purposes, 
or for applied uses like [Singularity Registry HPC](https://github.com/singularityhub/shpc-registry) 
to derive an "ideal" set of entrypoints per container.

## Usage

### Automated Updates

The cache here stores raw files that include path roots and files discovered within 
for [BioContainers](https://depot.galaxyproject.org/singularity/). This automation runs weekly and does the following:

- We install [shpc](https://github.com/singularityhub/singularity-hpc) and the [guts software])(https://github.com/singularityhub/guts)
- We run the [update_biocontainers.py](update_biocontainers.py) script that:
  - Parses the latest listing of containers from the [BioContainers Depot](https://depot.galaxyproject.org/singularity/)
  - Generate a unique list of containers and latest (first appearing) tag [^1].
  - Read in the [skips.json](skips.json) - a cached list of containers that we skip because their guts were not extractable [^2].
  - For every new identifier to add: 
   - Prepare a directory to store the new cache entry (a json file)
   - Use the [pipelib](https://vsoch.github.io/pipelib/getting_started/user-guide.html) software to sort tags and get the latest.
   - Use the guts [ManifestGenerator](https://singularityhub.github.io/guts/getting_started/user-guide.html#manifest) to retrieve a listing of paths and associated files within.
   - Filter out known patterns that are not executables of interest.
   - Write this output of aliases to the filesystem under the container identifier as a json file.
- After new aliases are added, [calculate_frequency.py](.github/scripts/calculate_frequency.py) is run to update global [counts.json](counts.json)

The result is alias-level data for each container, along with a global set of counts.

[^1]: For the step that grabs the "latest" tag, since the container URI (without any tag) can be used to get a listing of all tags, it isn't important to be correct to get the latest tag - this can be easily obtained later in a workflow from the unique resource identifier without a tag.  
[^2]: There are several reasons for skipping a container. One is that the guts software is not able to extract every set of container guts to the filesystem. A container that attempts to extract particular locations, or that takes up too much space for the GitHub runner will be skipped. Another reason is the pipelib software failing to filter a meaningful set of versioned tags and sort them (e.g., the listing comes back empty and there are no tags known to retrieve). In practice this is a small number as a percentage of the total.

### Singularity Registry HPC


As an example of the usage of this cache, we use these cache entries to populate 
the [Singularity HPC Registry](https://github.com/singualrityhub/shpc-registry).
On a high level, shpc-registry is providing install configuration files for containers.
Docker or other OCI registry containers are installed to an HPC system via module software,
and to make this work really well, we need to know their aliases. This is where data from
the cache comes in! Specifically for this use case this means we:

- Identify a new container, C, not in the registry from the executable cache here
- Create a set of global executable counts, G
- Define a set of counts from G in C as S
- Rank order S from least to greatest}
- Include any entries in S that have a frequency < 10
- Include any entries in S that have any portion of the name matching the container identifier
- Above that, add the next 10 executables with the lowest frequencies, and < 1,000

The frequencies are calculated across the cache here, included in [counts.json](counts.json).
This produces a container configuration file with a likely good set of executables that
represent the most unique to that container, based on data from the cache.

To learn more about Singularity Registry HPC you can:

- 📖️ Read the [documentation](https://singularity-hpc.readthedocs.io/en/latest/) 📖️
- ⭐️ Browse the [container module collection](https://singularityhub.github.io/shpc-registry/) ⭐️


## Contribution

This registry showcases a container executable cache, and specifically includes over 8K containers
from BioContainers. If you would like to add another source of container identifiers contributions are 
very much welcome! 

## License

This code is licensed under the MPL 2.0 [LICENSE](LICENSE).
