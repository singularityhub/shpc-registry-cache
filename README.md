# Shpc Registry Cache

This is a static cache of container executables discovered on the path. The cache is
updated once a week (Wednesday), and we store namespaced (based on OCI or Docker registry)
identifiers from the repository root here. Since we primarily cache the set of BioContainers,
that means the main set is under [quay.io](quay.io). These counts are useful for research purposes, 
or for applied uses like [Singularity Registry HPC](https://github.com/singularityhub/shpc-registry) 
to derive an "ideal" set of entrypoints per container. The cache is generated via the [container-executable-discovery](https://github.com/singularityhub/container-executable-discovery) action. For details about how
the cache algorithm works, see the action as the source of truth. A brief description
is included below.

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

## Manual Update

To update manually, install the updater:

```bash
$ python -m pip install git+https://github.com/vsoch/pipelib@main
$ python -m pip install git+https://github.com/singularityhub/guts@main
$ python -m pip install git+https://github.com/singularityhub/singularity-hpc@main
```
```bash
$ git clone --depth 1 https://github.com/singularityhub/container-executable-discovery
$ cd container-executable-discovery/lib
$ pip install -e .
```

Then generate the biocontainers listing file:

```bash
$ pip install -r .github/scripts/dev-requirements.txt
$ python .github/scripts/get_biocontainers.py /tmp/biocontainers.txt
```

And then run the update!

```bash
$ container-discovery update-cache --root $(pwd) --repo-letter-prefix --namespace quay.io/biocontainers /tmp/biocontainers.txt 
```

This is useful to run locally sometimes when there are huge containers that won't be extractable
in a GitHub action.

## Contribution

This registry showcases a container executable cache, and specifically includes over 8K containers
from BioContainers. If you would like to add another source of container identifiers contributions are 
very much welcome! 

## License

This code is licensed under the MPL 2.0 [LICENSE](LICENSE).
