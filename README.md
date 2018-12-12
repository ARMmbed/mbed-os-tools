# Mbed OS Tools

This repository contains the python modules needed to work with Mbed OS. **The APIs in this repository are not stable**, as indicated by the 0.x.x semantic version. For this reason, it is recommened to continue using the existing python packages, namely [mbed-ls](https://github.com/ARMmbed/mbed-ls), [mbed-host-tests](https://github.com/ARMmbed/htrun), and [mbed-greentea](https://github.com/ARMmbed/greentea).

To contribute changes to these packages, please commit them to this repository. The mapping of these packages to the `mbed-os-tools` modules is as follows:

- mbed-ls - `src/mbed_os_tools/detect` for the implementation, `test/detect` for the tests
- mbed-greentea - `src/mbed_os_tools/test` for the implementation, `test/test` for the tests
- mbed-host-tests - `src/mbed_os_tools/test` for the implementation, `test/test` for the tests

## License and contributions

The software is provided under [Apache-2.0 license](LICENSE). Contributions to this project are accepted under the same license. Please see [contributing.md](CONTRIBUTING.md) for more info.

This project contains code from other projects. The original license text is included in those source files. They must comply with our [license guide](https://os.mbed.com/docs/latest/reference/license.html)
