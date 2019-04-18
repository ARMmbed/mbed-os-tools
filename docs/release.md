# Mbed OS Tools

`mbed-os-tools` is the name of the unified tools pip package. From this codebase, we release the other pip packages:

- `mbed-ls` (Mbed LS): https://pypi.org/project/mbed-ls
- `mbed-host-tests` (htrun): https://pypi.org/project/mbed-host-tests
- `mbed-greentea` (greentea): https://pypi.org/project/mbed-greentea

## Package and API structure

`mbed-os-tools` exposes the following modules:

- `mbed_os_tools.detect` - All code contained within Mbed LS, used for detecting attached platforms
- `mbed_os_tools.test` - All code used to test platforms with the "greentea" framework
 - Will also need to plan ahead for icetea integration here

The other packages take these modules and expose the existing public API. (ex. `import mbed_lstools` for mbed-ls). The goal will be in the future to remove the other packages and just consolidate on the `mbed_os_tools.*` API exposed by `mbed-os-tools`. This path gives us the opportunity to deprecate the other packages to allow users to migrate.

## Versioning

The versions of the released packages (initially `mbed-ls`, `mbed-host-tests`, and `mbed-greentea`) will continue unaffected.
`mbed-os-tools` will be released initially as `0.x` indicating that the APIs are unstable. This will give us time to evolve the API and build up our processes. We don't intend to make API changes that often, but it may be necessary to do so in the first few releases.

When it comes time to drop the packages, `mbed-os-tools` will be released as stable (`1.0`). Before being released as stable, the following tasks should
be completed:

- All packages are marked as deprecated with a redirect to `mbed-os-tools`
  - The Python modules should also print deprecation messages when using the modules directly
- All documentation for `mbed-os-tools` needs to be delivered to the Mbed OS docs team for deployment to `os.mbed.com/docs`

## Releasing

![Release versioning](package_versioning.png)

The packages need to be released in the correct order. This is due to the new dependencies described above. Follow these steps to make a new release of the tools:

1. Release mbed-os-tools with a patch version increase
2. For each package, change the "mbed-os-tools" requirement version to the number just released (in this case it would be 0.0.1).
3. For each package, increase each patch number (this will vary with each package).
4. Release each package to pypi

The packages are uploaded to pypi using the [twine](https://github.com/pypa/twine) utility. Once your pypi credentials are setup, run the following commands in each package:

```
python setup.py sdist
twin upload dist/<package>.tar.gz
```

## Documentation

All public APIs are required to be fully documented with comments throughout the codebase. From these comments,
we will generate API documentation. There will also be examples and in-depth descriptions for higher-level concepts.
This documentation is strictly for the `mbed-os-tools` package, **NOT the other packages**. The other packages will
retain their current documentation (typically just a README in the project folder).

The documentation will be versioned with each release of `mbed-os-tools`. We plan to evolve the automated processes to generate
these documents as the repository matures. We plan to use GitHub Pages as a the main reference site while `mbed-os-tools` is in versions 0.x (unstable), but also as a staging site for our automated deliverables. When the package is released as 1.0 (stable), these generated documents will be delivered to the docs team for hosting on os.mbed.com/docs.
