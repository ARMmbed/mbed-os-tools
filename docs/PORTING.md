# Table of contents

* [Table of contents](#table-of-contents)
* [Using Greentea to test an mbed OS port](#using-greentea-to-test-an-mbed-os-port)
  * [Getting started](#getting-started)
    * [Test tools overview](#test-tools-overview)
      * [Greentea](#greentea)
      * [greentea-client](#greentea-client)
      * [htrun](#htrun)
      * [mbed-ls](#mbed-ls)
  * [Test tools installation dependencies](#test-tools-installation-dependencies)
    * [Test tools installation](#test-tools-installation)
    * [Using a virtual environment](#using-a-virtual-environment)
    * [Verifying test tools setup](#verifying-test-tools-setup)
  * [Test tools workflows](#test-tools-workflows)
    * [List connected platforms](#list-connected-platforms)
    * [Map your mbed platform with mbed-ls](#map-your-mbed-platform-with-mbed-ls)
      * [Checking if your platform is already supported by mbed-ls](#checking-if-your-platform-is-already-supported-by-mbed-ls)
    * [Building your project](#building-your-project)
      * [Full build and test workflow](#full-build-and-test-workflow)
      * [Filtering tests](#filtering-tests)
    * [Running one test binary with htrun](#running-one-test-binary-with-htrun)
    * [Interpreting test results](#interpreting-test-results)
      * [Terms used in `htrun` and `Greentea` output](#terms-used-in-htrun-and-greentea-output)
      * [Test suite results report](#test-suite-results-report)
      * [Test cases results](#test-cases-results)

# Using Greentea to test an mbed OS port

When you're porting your platform to mbed OS, it helps to test as you go. Greentea, the mbed test tools suite, is perfectly suited for this purpose.

This guide walks you through the basic setup and workflows you'll need to test your mbed OS port.

## Getting started

How to set up the test tools for your new platform.

### Test tools overview

The ```mbed ```  test tools collection includes:
* [Greentea](https://github.com/ARMmbed/greentea) - the mbed test automation framework, allowing test suite execution inside your project. Distributed as a Python Package: [mbed-greentea in PyPI](https://pypi.python.org/pypi/mbed-greentea).
* [greentea-client](https://github.com/ARMmbed/greentea-client) - Greentea's device under test (DUT) side C++ library. The public API can be found [here](https://github.com/ARMmbed/htrun#greentea-client-api).
* [htrun](https://github.com/ARMmbed/htrun) - the test runner for the mbed test suite. Distributed as a Python Package: [mbed-host-tests in PyPI](https://pypi.python.org/pypi/mbed-host-tests).
* [mbed-ls](https://github.com/ARMmbed/mbed-ls) - list all mbed-compatible devices connected to the host. Distributed as a Python Package: [mbed-ls in PyPI](https://pypi.python.org/pypi/mbed-ls).

To install all tools, see [below](test-tools-installation).

#### Greentea
"Generic Regression EnvironmENt for TEst Automation" for mbed-enabled platforms. You can use this application to execute groups of tests, generate reports and check for regressions.

This application is available as a command line tool called `mbedgt` and an importable Python 2.7 library:

* [Python Package](https://pypi.python.org/pypi/mbed-greentea).
* [Greentea source code](https://github.com/ARMmbed/greentea).


The installation guide is [here](https://github.com/ARMmbed/greentea#installing-greentea).

#### greentea-client

The C/C++ DUT (Device Under Test) side of the Greentea test suite. You can use this library to instrument your test cases so they work with Greentea. This library will allow your DUT to communicate with Greentea and host tests.

You can obtain this library using one of the following methods:

* [greentea-client library on GitHub](https://github.com/ARMmbed/greentea-client)
* [greentea-client as a yotta module](https://yotta.mbed.com/#/module/greentea-client/1.1.0).

This library is available in your C/C++ environment by using `#include "greentea-client/test_env.h"`.

#### htrun

Use `htrun` to flash, reset and perform host-supervised tests on mbed-enabled platforms. Greentea uses this application to instrument test binary execution (flashing, platform resetting and instrumenting test cases). You can also use this application to manually trigger test binary execution.

This application is available as a command line tool called `mbedhtrun` and an importable Python 2.7 library:

* [htrun source code](https://github.com/ARMmbed/htrun).
* [Python Package](https://pypi.python.org/pypi/mbed-host-tests).

The installation guide is [here](https://github.com/ARMmbed/htrun#installation).


#### mbed-ls
`mbedls` is a set of tools used to detect mbed-enabled platforms on the host OSs: Windows 7 onwards, Ubuntu (and most other distributions of Linux) and Mac OS.

This application is available as a command line tool called `mbedls` and an importable Python 2.7 library:

* [mbed-ls source code](https://github.com/ARMmbed/mbed-ls).
* [Python Package](https://pypi.python.org/pypi/mbed-ls).

Installation guide is [here](https://github.com/ARMmbed/mbed-ls#installation).

## Test tools installation dependencies

All test tools are implemented with and use Python 2.7.11; [it is available here](https://www.python.org/downloads/release/python-2711/).

You'll need to add the following modules:
  * [Pip](https://pypi.python.org/pypi/pip). If you installed Python 2.7.11, you should already have pip; run `$ pip --version` to make sure.
  * [setuptools](https://pythonhosted.org/an_example_pypi_project/setuptools.html) to install dependencies.

.

For mbed-enabled platforms you may need to install additional serial port drivers.  Please follow the installation instructions [here](https://developer.mbed.org/handbook/Windows-serial-configuration).



Optional: If you want to install test tools directly from sources, install [Git](https://git-scm.com/downloads)

### Test tools installation

Installation of test tools will include installation of `Greentea`, `htrun` and `mbed-ls`:
```
$ pip install mbed-greentea --upgrade
```

This installs all Python package dependencies along with the required mbed test tools. No additional steps are necessary if this installation is successful.

### Using a virtual environment

Our test tools are mainly written in Python (2.7). If your project or Continuous Integration job uses Python tools and Python packages extensively, installing our test tools directly on the same machine may cause Python dependency collision. To avoid unnecessary hassle, you can use a virtual environment. This keeps Python projects - and their package dependencies - in separate places.

For more details about Python's virtual environment please check [Virtual Environments](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

### Verifying test tools setup

You can use the `pip list` command to check if the mbed test tools are installed on your system correctly:
```
$ pip list
mbed-greentea==0.2.18
mbed-host-tests==0.2.14
mbed-ls==0.2.10
```

You can see that all required packages (`mbed-greentea`, `mbed-host-tests` and `mbed-ls`) are present in the `0.2.x` (latest) versions.

Alternatively, you can call the tools with the ``--version`` option::
```
$ mbedgt --version
```
```
$ mbedhtrun --version
```
```
$ mbedls --version
```

## Test tools workflows

This chapter presents the most common workflows for using the mbed test tools.

### List connected platforms

To list all platforms connected to your host computer, please use the `mbedls` command:
```
$ mbedls
+---------------+----------------------+-------------+-------------+----------------------+-----------------+
| platform_name | platform_name_unique | mount_point | serial_port | target_id            | daplink_version |
+---------------+----------------------+-------------+-------------+----------------------+-----------------+
| K64F          | K64F[0]              | E:          | COM228      | 02400000293049769900 | 0241            |
| K64F          | K64F[1]              | H:          | COM230      | 02400000335149769900 | 0241            |
+---------------+----------------------+-------------+-------------+----------------------+-----------------+
```

`mbedls` reports the following for each mbed enabled platform:
* `platform_name`: the canonical platform name used across our build systems and test tools.
* `mount_point` : where the mbed-enabled platform's MSD ismounted. The mount point is used to flash binaries onto the platform.
* `serial_port`: where the mbed-enabled platform's CDC is mounted. The serial port is used for communication between the device and the host while tests execute. The serial port is also used to reset platforms by sending a serial break.
* `target_id`: a unique ASCII HEX identifier used to distinguish between platforms.
* `daplink_version`: the DAPLink or Interface Chip version.

Note that our test tools use `mbedls` to detect platforms for the automation process, which requires us to:
* Detect all available platforms.
* Allocate platform(s) for testing by Greentea application.
* Determine platform presence in the system while testing, using a unique target ID.

### Map your mbed platform with mbed-ls

If your platform is not detected, for example `target_id` can't be mapped to `platform_name`, you may want to mock - or temporarily map - `target_id` to your custom platform name (`platform_name`).

You can use [these instructions](https://github.com/ARMmbed/mbed-ls#mocking-new-or-existing-target-to-custom-platform-name) to configure `mbed-ls` to remap `target_id` to custom platforms name.

<span class="notes">**Note:** Please make sure that you remap your platform to a name that is not currently in use by our tools. See the next section for instructions for listing all current platform names.</span>

#### Checking if your platform is already supported by mbed-ls

```
$ mbedls --list
+------------------+----------------------+
| target_id_prefix | platform_name        |
+------------------+----------------------+
  ....
| 0183             | UBLOX_C027           |
| 0200             | KL25Z                |
| 0231             | K22F                 |
| 0240             | K64F                 |
  ....
| 9009             | ARCH_BLE             |
| 9900             | NRF51_MICROBIT       |
+------------------+----------------------+
```

``--list`` prints a list of all the platforms `mbed-ls` is familiar with, and maps the `target_id` to the `platform_name`.

<span class="notes">**Note:** The `target_id_prefix` prefix is four characters long and shows your `target_id` vendor and platform IDs.</span>

### Building your project

You need to use your build system to build a project. You can use [the yotta](http://yottadocs.mbed.com) build system if your project is encapsulated in a `yotta` module.

If you're not using yotta, you can use any other build system that supports [test specification files](https://github.com/ARMmbed/greentea#test-specification-json-formatted-input). You can also create the test specification files manually if necessary.

#### Full build and test workflow

The build and test workflow:

1. Invoke a build system:
```
$ build ...
```
1. The build system compiles and builds all libraries, code and tests. While building tests, the build system should automatically generate a test specification file called `test_spec.json` (or you will need to create it manually). This file is automatically read and loaded if it exists in the current directory (the directory in which `Greentea` is invoked).
For more details on how to use the command line, refer to the instructions [here](https://github.com/ARMmbed/greentea#command-line-usage)

1. Call `Greentea` to [list all built test binaries](https://github.com/ARMmbed/greentea#command-line-usage):
```
$ mbedgt --list
```

1. Call `Greentea` to execute all tests:
```
$ mbedgt -V
```
.
<span class="notes">**Note:** This may take a while, and you probably do not want to run all your tests at once. You may want to filter for tests by names and use the command line switch `-n`, as explained below.</span>

#### Filtering tests

To filter for tests by names, use comma separated test case names with the command line option `-n`:
```
$ mbedgt -V -n test-case-name-basic,test-case-name-rtos
```

<span class="tips">**Tips:** Read more [here](https://github.com/ARMmbed/greentea#cherry-pick-group-of-tests.</span>

To filter for a group of tests, filter test case names with the command line option `-n` and the suffix `*`. For example, to filter for all tests with a name that contains  `<test-case-name>...`:
```
$ mbedgt -V -n test-case-name*
```

<span class="tips">Read more [here](https://github.com/ARMmbed/greentea#cherry-pick-tests).</span>

### Running one test binary with htrun

While executing each test binary Greentea will explicitly pass control to and call `htrun` (the command line tool name is `mbedhtrun`).

Here is a Greentea log with the command line tool calling `mbedhtrun`:
```
mbedgt: selecting test case observer...
        calling mbedhtrun: mbedhtrun -d E: -p COM228:9600 -f ".build\tests\K64F\GCC_ARM\TESTS\mbedmicro-rtos-mbed\mail\TESTS-mbedmicro-rtos-mbed-mail.bin" -C 4 -c shell -m K64F -t 0240000029304e450038500878a3003cf131000097969900
```

Greentea uses the following command to call `mbedhtrun`:
```
$ mbedhtrun -d E: -p COM228:9600 -f ".build\tests\K64F\GCC_ARM\TESTS\mbedmicro-rtos-mbed\mail\TESTS-mbedmicro-rtos-mbed-mail.bin" -C 4 -c shell -m K64F -t 0240000029304e450038500878a3003cf131000097969900
```
Where:
* `-d E:`: the definition of the mount point that will be used to flash the DUT.
* `-p COM228:9600`: the definition of the serial port (with baudrate) used for communicating with the DUT.
* `-f ".build\tests\K64F\GCC_ARM\TESTS\mbedmicro-rtos-mbed\mail\TESTS-mbedmicro-rtos-mbed-mail.bin"`: the path to the image we will flash to the DUT.
* `-C 4`: the time we will wait after the device is flashed. This time may vary depending on the platform.
* `-c shell`: the method used to copy the binary onto the DUT mount point.
* `-m K64F`: the platform name (currently not used).
* `-t 0240000029304e450038500878a3003cf131000097969900`: the TargetID of the platform we will use. This useful option is passed by `Greentea` to `htrun` during the auto-detection of test-compatible platforms. Greentea uses `mbed-ls` to list all compatible platforms (by platform names) and maps them to TargetID.

You can use this command, with a few modifications, to reproduce a binary test run (flash, reset and test execution).

<span class="tips">**Tip:** Use the `--skip-flashing` flag of `mbedhtrun` to skip the flashing phase if you already have the same binary on your platform.</span>

### Interpreting test results

#### Terms used in `htrun` and `Greentea` output

Please check [this link](https://github.com/ARMmbed/greentea-client#terms) for details, especially [test suite](https://github.com/ARMmbed/greentea-client#test-suite) and [test case](https://github.com/ARMmbed/greentea-client#test-case).



#### Test suite results report

The test suite report describes the state of the test binary after all the test procedures finished. In general, the report returns one of three states:
* `OK`: All the tests passed.
* `FAIL`: The test binary itself behaved as expected, but some test cases or test code assertions failed.
* An undefined state that can manifest itself as many other erroneous states (such as  `ERROR` or `TIMEOUT`): something went wrong with the binary itself, or the test mechanism inside the binary failed to instrument test code.

```
mbedgt: test suite report:
+--------------+---------------+----------------------------------+--------+--------------------+-------------+
| target       | platform_name | test suite                       | result | elapsed_time (sec) | copy_method |
+--------------+---------------+----------------------------------+--------+--------------------+-------------+
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | FAIL   | 13.3               | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-dev_null      | OK     | 13.14              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-echo          | FAIL   | 41.08              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-generic_tests | OK     | 12.11              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-rtc           | OK     | 21.6               | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-stl_features  | OK     | 12.87              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker        | OK     | 22.08              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker_2      | OK     | 22.04              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker_3      | OK     | 22.07              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-timeout       | OK     | 22.06              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-wait_us       | OK     | 20.96              | shell       |
+--------------+---------------+----------------------------------+--------+--------------------+-------------+
mbedgt: test suite results: 2 FAIL / 9 OK
```

#### Test cases results

Some test suites (test binaries) may use our test harness, called [utest](https://github.com/ARMmbed/utest). `utest` allows users to write a set of test cases inside one binary and report results for each test case separately. Each test case may report `OK`, `FAIL` or `ERROR`.

```
mbedgt: test case report:
+--------------+---------------+----------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| target       | platform_name | test suite                       | test case                           | passed | failed | result | elapsed_time (sec) |
+--------------+---------------+----------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %e %E float formatting   | 1      | 0      | OK     | 1.01               |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %f %f float formatting   | 0      | 1      | FAIL   | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %g %g float formatting   | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %i %d integer formatting | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %u %d integer formatting | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %x %E integer formatting | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: strpbrk                  | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: strtok                   | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-dev_null      | tests-mbed_drivers-dev_null         | 1      | 0      | OK     | 13.14              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-echo          | Echo server: x16                    | 1      | 0      | OK     | 16.54              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-echo          | Echo server: x32                    | 0      | 0      | ERROR  | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-generic_tests | Basic                               | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-generic_tests | Blinky                              | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-generic_tests | C++ heap                            | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-generic_tests | C++ stack                           | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-rtc           | RTC strftime                        | 1      | 0      | OK     | 10.14              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-stl_features  | STL std::equal                      | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-stl_features  | STL std::sort abs                   | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-stl_features  | STL std::sort greater               | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-stl_features  | STL std::transform                  | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker        | Timers: 2 x tickers                 | 1      | 0      | OK     | 11.15              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker_2      | Timers: 1x ticker                   | 1      | 0      | OK     | 11.15              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker_3      | Timers: 2x callbacks                | 1      | 0      | OK     | 11.15              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-timeout       | Timers: toggle on/off               | 1      | 0      | OK     | 11.15              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-wait_us       | Timers: wait_us                     | 1      | 0      | OK     | 10.14              |
+--------------+---------------+----------------------------------+-------------------------------------+--------+--------+--------+--------------------+
mbedgt: test case results: 1 FAIL / 23 OK / 1 ERROR
mbedgt: completed in 223.55 sec
mbedgt: exited with code 2
```


