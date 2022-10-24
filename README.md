# Shpc Registry Cache

This cache stores the raw files for biocontainers, and (eventually) will be updated nightly.
Eventually we will be able to derive an "ideal" set of entrypoints per container by way of:

- Subsetting to those in a container, including counts
- Rank ordering
- Including any counts with a frequency < 10
- Above that, including the next N

With numbers to be determined! We will then be able to generate the container
registry files for shpc with these entrypoints TBA.

