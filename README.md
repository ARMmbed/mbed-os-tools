[![Circle CI](https://circleci.com/gh/ARMmbed/greentea.svg?style=svg)](https://circleci.com/gh/ARMmbed/greentea)
[![Coverage Status](https://coveralls.io/repos/github/ARMmbed/greentea/badge.svg?branch=master)](https://coveralls.io/github/ARMmbed/greentea?branch=master)
[![PyPI version](https://badge.fury.io/py/mbed-greentea.svg)](https://badge.fury.io/py/mbed-greentea)

# Greentea - test automation for mbed
_**G**eneric **Re**gression **En**vironment for **te**st **a**utomation_

## Introduction

Greentea is the automated testing tool used for mbed OS development. It automates the process of flashing mbeds, driving the test, and accumulating test results into test reports. It is designed to be used by developers for local development as well as for automation in a Continuous Integration environment.

This document should help you get started using Greentea. It doesn't cover the technical details of the interactions between the platform and the host machine. Please see the [htrun documentation](https://github.com/ARMmbed/htrun) (the tool used by Greentea to drive tests) for more information on this topic.

### Prerequistes

Greentea requires [Python version 2.7](https://www.python.org/downloads/) to run. It supports the following OSes:

- Windows
- Linux (Ubuntu preferred)
- OSX (experimental)

### Installing

Greentea is usually installed by other tools that depend on it. You can see if it is already installed by running:
```
$ mbedgt --version
1.2.5
```

It can also be installed manually via pip.

```
pip install mbed-greentea
```

## Test specification JSON format

The Greentea test specification format allows the test automation to be build system agnostic. It provides important data like test names, paths to test binaries, and on which platform the binaries should run.

Greentea will automatically look for files called `test_spec.json` in your working directory. You can also use the `--test-spec` argument to direct Greentea to a specific test specification file.

When the `-t` / `--target` argument is used with the `--test-spec` argument, it can be used to select which "build" should be used. In the example given below, you could provide the arguments `--test-spec test_spec.json -t K64F-ARM` to only run that build's tests.

### Example of test specification file

In the below example there are two builds defined:
* Build `K64F-ARM` for NXP `K64F` platform compiled with `ARMCC` compiler and
* build `K64F-GCC` for NXP `K64F` platform compiled with `GCC ARM` compiler.

```json
{
    "builds": {
        "K64F-ARM": {
            "platform": "K64F",
            "toolchain": "ARM",
            "base_path": "./BUILD/K64F/ARM",
            "baud_rate": 9600,
            "tests": {
                "tests-mbedmicro-rtos-mbed-mail": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": "./BUILD/K64F/ARM/tests-mbedmicro-rtos-mbed-mail.bin"
                        }
                    ]
                },
                "tests-mbed-drivers-c_strings": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": "./BUILD/K64F/ARM/tests-mbed-drivers-c_strings.bin"
                        }
                    ]
                }
            }
        },
        "K64F-GCC": {
            "platform": "K64F",
            "toolchain": "GCC_ARM",
            "base_path": "./BUILD/K64F/GCC_ARM",
            "baud_rate": 9600,
            "tests": {
                "tests-mbedmicro-rtos-mbed-mail": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": "./BUILD/K64F/GCC_ARM/tests-mbedmicro-rtos-mbed-mail.bin"
                        }
                    ]
                }
            }
        }
    }
}
```

In below examples we will use the above test specification file.

## Command line usage
Here we will highlight a few of the capabilities of the Greentea command line interface. For a full list of the availble options, please run `mbedgt --help`.

We will assume for the examples below that the above `test_spec.json` file is in current directory.

### Listing all tests
We can use the `-l` arguement to list all availble tests:

```
$ mbedgt -l
mbedgt: using 'test_spec.json' from current directory!
mbedgt: available tests for built 'K64F-ARM', location './BUILD/K64F/ARM'
        test 'tests-mbedmicro-rtos-mbed-mail'
        test 'tests-mbed-drivers-c_strings'
mbedgt: available tests for built 'K64F-GCC', location './BUILD/K64F/GCC_ARM'
        test 'tests-mbedmicro-rtos-mbed-mail'
```

### Executing all tests
The default action of greentea is to execute all tests that were found. We also add `-V` to make the output more verbose:

```
$ mbedgt -V
mbedgt: greentea test automation tool ver. 1.2.5
...
mbedgt: test case results: 3 OK
mbedgt: completed in 60.00 sec
```

### Limiting tests
We can select test cases by name using the `-n` argument. The below command will execute all tests named `tests-mbedmicro-rtos-mbed-mail` from all builds in the test specification:
```
$ mbedgt -V -n tests-mbedmicro-rtos-mbed-mail
```

When using the `-n` argument, you can use the `*` character at the end of a test name to match all tests that share a prefix. This command will execute all tests that start with `tests*`:

```
$ mbedgt -V -n tests*
```

We can use the `-t` argument to select which build to use when finding tests. This command will execute the test `tests-mbedmicro-rtos-mbed-mail` for the `K64F-ARM` build in the test specification:
```
$ mbedgt -V -n tests-mbedmicro-rtos-mbed-mail -t K64F-ARM
```

You can use a comma (`,`) to separate test names (argument `-n`) and build names (argument `-t`). This command will execute the tests `tests-mbedmicro-rtos-mbed-mail` and `tests-mbed-drivers-c_strings` for the `K64F-ARM` and `K64F-GCC_ARM` builds in the test specification:
```
$ mbedgt -V -n tests-mbedmicro-rtos-mbed-mail,tests-mbed-drivers-c_strings -t K64F-ARM,K64F-GCC_ARM
```

### Selecting platforms
You can limit which boards Greentea should use for testing by using the `--use-tids` argument.

```
$ mbedgt --use-tids 02400203C3423E603EBEC3D8,024002031E031E6AE3FFE3D2
```

Where ```02400203C3423E603EBEC3D8``` and ```024002031E031E6AE3FFE3D2``` are the target IDs of platforms attached to your system.

Target IDs can be viewed by using the [mbed-ls](https://github.com/ARMmbed/mbed-ls) tool (installed with Greentea).

```
$ mbedls
+--------------+---------------------+------------+------------+-------------------------+
|platform_name |platform_name_unique |mount_point |serial_port |target_id                |
+--------------+---------------------+------------+------------+-------------------------+
|K64F          |K64F[0]              |E:          |COM160      |024002031E031E6AE3FFE3D2 |
|K64F          |K64F[1]              |F:          |COM162      |02400203C3423E603EBEC3D8 |
|LPC1768       |LPC1768[0]           |G:          |COM5        |1010ac87cfc4f23c4c57438d |
+--------------+---------------------+------------+------------+-------------------------+
```
In this case, one target - the LPC1768 - won’t be tested.

### Creating reports
Greentea supports a number of report formats.

#### HTML
This creates an interactive HTML page with test results and logs.
```
mbedgt --report-html html_report.html
```

#### JUnit
This creates a XML JUnit report which can be used with popular Continuous Integration software like [Jenkins](https://jenkins.io/index.html).
```
mbedgt --report-junit junit_report.xml
```

#### JSON
This creates a general JSON report.
```
mbedgt --report-json json_report.json
```

#### Plain text
This creates a human-friendly text summary of the test run.
```
mbedgt --report-text text_report.text
```

## Host test detection
When developing with mbed OS, Grentea will detect host tests automatically if they placed in the correct location. All tests in mbed OS are placed under a `TESTS` directory. You may place custom host test scripts in a folder named `host_tests` in this folder. For more information on the mbed OS test directory structure, please see the [mbed CLI documentation](https://docs.mbed.com/docs/mbed-os-handbook/en/latest/dev_tools/cli/#test-directory-structure)

## Common issues

### `IOERR_SERIAL` errors
This can be caused by a number of things:
- The serial port is in use by another program. Be sure all terminals and other instances of Greentea are closed before trying again
- The mbed's interface firmware is out of date. Please see the platform's page on [developer.mbed.org](https://developer.mbed.org/) for details on how to update it
