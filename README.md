# Mbed Tools

This repository contains the python modules needed to work with Mbed OS. **The APIs in this repository are not stable**, as indicated by the 0.x.x semantic version. For this reason, it is recommened to continue using the existing python packages, namely [mbed-ls](https://github.com/ARMmbed/mbed-ls), [mbed-host-tests](https://github.com/ARMmbed/htrun), and [mbed-greentea](https://github.com/ARMmbed/greentea).

To contribute changes to these packages, please commit them to this repository. The mapping of these packages to the `mbed-tools` modules is as follows:

- mbed-ls - `mbed_tools/detect` for the implementation, `test/detect` for the tests
- mbed-greentea - `mbed_tools/test` for the implementation, `test/test` for the tests
- mbed-host-tests - `mbed_tools/test` for the implementation, `test/test` for the tests

