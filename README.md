# Shpc Registry Cache

This cache stores the raw files for biocontainers, and is updated weekly.
We can use these counts for research purposes, or to derive an "ideal" set of entrypoints per container by way of:

- Subsetting to those in a container, including counts
- Rank ordering from least to greatest (lower frequency is a more unique command)
- Including any counts with a frequency < 10
- Above that, including the next N

With numbers to be determined! We will then be able to generate the container
registry files for shpc with these entrypoints TBA.
