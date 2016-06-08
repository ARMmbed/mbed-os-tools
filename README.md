[![Circle CI](https://circleci.com/gh/ARMmbed/greentea.svg?style=svg)](https://circleci.com/gh/ARMmbed/greentea)
[![Coverage Status](https://coveralls.io/repos/github/ARMmbed/greentea/badge.svg?branch=master)](https://coveralls.io/github/ARMmbed/greentea?branch=master)
[![PyPI version](https://badge.fury.io/py/mbed-greentea.svg)](https://badge.fury.io/py/mbed-greentea)

# Table of contents

* [Table of contents](#table-of-contents)
* [Introduction](#introduction)
* [Quickstart document](#quickstart-document)
  * [mbed test tools collection](#mbed-test-tools-collection)
  * [Additional documentation](#additional-documentation)
  * [Supported operating systems](#supported-operating-systems)
* [Getting started](#getting-started)
  * [End to end example](#end-to-end-example)
    * [Dependencies installation procedure](#dependencies-installation-procedure)
    * [Example test procedure walk-through](#example-test-procedure-walk-through)
  * [mbed test tools detailed list of dependencies](#mbed-test-tools-detailed-list-of-dependencies)
  * [Installing Greentea](#installing-greentea)
    * [Installation from PyPI (Python Package Index)](#installation-from-pypi-python-package-index)
    * [Installation from Python sources](#installation-from-python-sources)
    * [Virtual Environments (Python)](#virtual-environments-python)
      * [How to get and install virtualenv](#how-to-get-and-install-virtualenv)
      * [Basic Usage](#basic-usage)
      * [virtualenv example usage - Windows environment](#virtualenv-example-usage---windows-environment)
  * [Environment check](#environment-check)
  * [Building the mbed-drivers for yotta target target](#building-the-mbed-drivers-for-yotta-target-target)
* [Testing](#testing)
* [Test specification JSON formatted input](#test-specification-json-formatted-input)
  * [Test specification formatted](#test-specification-formatted)
  * [Example of test specification file](#example-of-test-specification-file)
    * [Command line usage](#command-line-usage)
      * [Executing all tests](#executing-all-tests)
      * [Cherry-pick tests](#cherry-pick-tests)
      * [Cherry-pick group of tests](#cherry-pick-group-of-tests)
* [Using Greentea with new targets](#using-greentea-with-new-targets)
  * [Greentea and yotta targets](#greentea-and-yotta-targets)
  * [Prototyping support](#prototyping-support)
    * [How to add board-target bindings for Greentea](#how-to-add-board-target-bindings-for-greentea)
    * [Prototyping or porting - sample workflow](#prototyping-or-porting---sample-workflow)
* [Selecting boards for test running](#selecting-boards-for-test-running)
  * [Option --use-tids example](#option---use-tids-example)
* [Additional features](#additional-features)
  * [Dynamic host test loader](#dynamic-host-test-loader)
  * [yotta config parse](#yotta-config-parse)
  * [Local yotta targets scan for mbed-target keywords](#local-yotta-targets-scan-for-mbed-target-keywords)
* [Common Issues](#common-issues)
  * [Uninstalling Greentea](#uninstalling-greentea)
* [Commissioning mbed platforms](#commissioning-mbed-platforms)

# Introduction

Hello and welcome to the mbed SDK test suite, codename *Greentea*. The test suite is a collection of tools that enable automated testing on mbed boards.

In its current configuration, the mbed test suite can automatically detect most of the popular mbed-enabled boards connected to the host over USB. The test suite uses the ```mbed-ls``` module to check for connected devices. A separate module called ```mbed-host-tests``` is used to flash and supervise each board's test. This decoupling allows us to make better software and maintain each of the functionalities as a separate domain.

# Quickstart document

Please read [QUICKSTART.md](https://github.com/ARMmbed/greentea/blob/master/docs/QUICKSTART.md) document if you want to familiarize yourself with top level features of ```Greentea`` mbed test tools.

## mbed test tools collection

```mbed ```  test tools set:
* [Greentea](https://github.com/ARMmbed/greentea) - mbed test automation framework, instrument test suite execution inside your yotta module.
  * This application is also distributed as Python Package: [mbed-greentea in PyPI](https://pypi.python.org/pypi/mbed-greentea).
* [greentea-client](https://github.com/ARMmbed/greentea-client) - ```Greentea``'s device side, C++ library.
  * This application is also distributed as yotta module: [greentea-client](https://yotta.mbed.com/#/module/greentea-client/0.1.8).
* [htrun](https://github.com/ARMmbed/htrun) - test runner for mbed test suite.
  * This application is also distributed as Python Package: [mbed-host-tests in PyPI](https://pypi.python.org/pypi/mbed-host-tests).
* [mbed-ls](https://github.com/ARMmbed/mbed-ls) - list all connected to host mbed compatible devices.
  * This application is also distributed as Python Package: [mbed-ls in PyPI](https://pypi.python.org/pypi/mbed-ls).

## Additional documentation

* [Quickstart document](https://github.com/ARMmbed/greentea/blob/master/docs/QUICKSTART.md)
* Things you need to know [when you contribute](https://github.com/ARMmbed/greentea/blob/master/docs/CONTRIBUTING.md) to open source mbed test tools repositories.

## Supported operating systems

* Windows 7
* Ubuntu LTS
* Linux (experimental)
* OS X 10.10 (experimental)

# Getting started

To use the mbed test suite you must:

* Install the dependencies.
* Download and install the mbed test suite.
* Build the mbed project sources.
* (Optional) you can take advantage of Python's [virtualenv](#virtual-environments-python) to install and run our test tools in virtual environment.

## End to end example
This end to end example shows how to install and use Greentea with an example mbed repository.
Example will assume that you:
* Have one mbed board connected to your PC over USB. In our case it will be one [Freescale K64F](https://developer.mbed.org/platforms/FRDM-K64F/) board.
* Installed toolchain for ARM Cortex-M: [GCC ARM Embedded v4.9.3](https://launchpad.net/gcc-arm-embedded).
* Installed source control client: [Git](https://git-scm.com/downloads).
* Installed Python: [Python 2.7.11](https://www.python.org/download/releases/2.7/).
* Installed build tools: [yotta](https://github.com/ARMmbed/yotta):
* You will need connection to Internet.

### Dependencies installation procedure

* Installing ```yotta``` build system:
```
$ pip install yotta --upgrade
```
* Installing ```Greentea``` test automation tools:
```
$ pip install mbed-greentea --upgrade
```
* Create a local clone of the GitHub [mbed-drivers](https://github.com/ARMmbed/mbed-drivers) repository.

### Example test procedure walk-through

Test tools installation should be completed already. Now we will show how we can test ```mbed-drivers``` repository using ```Greentea``` automates test tools:

* Go to your working directory and clone ```mbed-drivers``` repository:
```
$ git clone https://github.com/ARMmbed/mbed-drivers.git
$ cd mbed-drivers
```
* (Optional) Make sure your mbed device is compatible with available ```K64F``` yotta targets:
```bash
$ yotta --plain search -k mbed-target:k64f target --short
frdm-k64f-gcc 0.2.0: Official mbed build target for the mbed frdm-k64f development board.
frdm-k64f-armcc 0.1.4: Official mbed build target for the mbed frdm-k64f development board, using the armcc toolchain.
```

* Set the ```yotta``` build [target](http://yottadocs.mbed.com/tutorial/targets.html) to ```frdm-k64f-gcc```:
```
$ yotta target frdm-k64f-gcc
```
* Build the ```mbed-drivers``` module with yotta (note that ```Greentea``` can do this for you also automatically):
```
$ yotta build
```
* List the built test cases:
```bash
$ mbedgt --list
mbedgt: available tests for built targets, location 'c:\Work\mbed-drivers\build'
        target 'frdm-k64f-gcc':
        test 'mbed-drivers-test-c_strings'
        test 'mbed-drivers-test-dev_null'
        test 'mbed-drivers-test-echo'
        test 'mbed-drivers-test-generic_tests'
        test 'mbed-drivers-test-rtc'
        test 'mbed-drivers-test-stl_features'
        test 'mbed-drivers-test-ticker'
        test 'mbed-drivers-test-ticker_2'
        test 'mbed-drivers-test-ticker_3'
        test 'mbed-drivers-test-timeout'
        test 'mbed-drivers-test-wait_us'
```
* And finally - test (```-V``` is used to activate test case verbose mode):
```
$ mbedgt -VS
...
[1458047568.17][HTST][INF] No events in queue
[1458047568.17][HTST][INF] stopped consuming events
[1458047568.17][HTST][INF] host test result() call skipped, received: True
[1458047568.17][HTST][WRN] missing __exit event from DUT
[1458047568.17][HTST][INF] calling blocking teardown()
[1458047568.17][HTST][INF] teardown() finished
[1458047568.17][HTST][INF] {{result;success}}
mbedgt: checking for GCOV data...
mbedgt: mbed-host-test-runner: stopped
mbedgt: mbed-host-test-runner: returned 'OK'
mbedgt: test on hardware with target id: 0240000033514e450041500585d40043e981000097969900
mbedgt: test suite 'mbed-drivers-test-ticker' ........................................................ OK in 21.20 sec
        test case: 'Timers: 2 x tickers' ............................................................. OK in 11.03 sec
mbedgt: test case summary: 1 pass, 0 failures
mbedgt: all tests finished!
mbedgt: shuffle seed: 0.3028454009
mbedgt: test suite report:
+---------------+---------------+---------------------------------+--------+--------------------+-------------+
| target        | platform_name | test suite                      | result | elapsed_time (sec) | copy_method |
+---------------+---------------+---------------------------------+--------+--------------------+-------------+
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | FAIL   | 12.77              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-dev_null      | OK     | 11.58              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-echo          | FAIL   | 19.96              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-generic_tests | OK     | 10.99              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-rtc           | OK     | 21.0               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stl_features  | OK     | 11.73              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker        | OK     | 21.2               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker_2      | OK     | 21.18              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker_3      | OK     | 21.21              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-timeout       | OK     | 21.49              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-wait_us       | OK     | 20.14              | shell       |
+---------------+---------------+---------------------------------+--------+--------------------+-------------+
mbedgt: test suite results: 2 FAIL / 9 OK
mbedgt: test case report:
+---------------+---------------+---------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| target        | platform_name | test suite                      | test case                           | passed | failed | result | elapsed_time (sec) |
+---------------+---------------+---------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %e %E float formatting   | 1      | 0      | OK     | 0.07               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %f %f float formatting   | 0      | 1      | FAIL   | 0.3                |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %g %g float formatting   | 1      | 0      | OK     | 0.06               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %i %d integer formatting | 1      | 0      | OK     | 0.06               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %u %d integer formatting | 1      | 0      | OK     | 0.06               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %x %E integer formatting | 1      | 0      | OK     | 0.07               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: strpbrk                  | 1      | 0      | OK     | 0.04               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: strtok                   | 1      | 0      | OK     | 0.05               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-dev_null      | dev_null                            | 1      | 0      | OK     | 11.58              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-echo          | Echo server: x16                    | 1      | 0      | OK     | 1.6                |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-echo          | Echo server: x32                    | 0      | 0      | ERROR  | 0.0                |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-generic_tests | Basic                               | 1      | 0      | OK     | 0.03               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-generic_tests | Blinky                              | 1      | 0      | OK     | 0.04               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-generic_tests | C++ heap                            | 1      | 0      | OK     | 0.1                |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-generic_tests | C++ stack                           | 1      | 0      | OK     | 0.15               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-rtc           | RTC strftime                        | 1      | 0      | OK     | 10.43              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stl_features  | STL std::equal                      | 1      | 0      | OK     | 0.04               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stl_features  | STL std::sort abs                   | 1      | 0      | OK     | 0.03               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stl_features  | STL std::sort greater               | 1      | 0      | OK     | 0.05               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stl_features  | STL std::transform                  | 1      | 0      | OK     | 0.05               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker        | Timers: 2 x tickers                 | 1      | 0      | OK     | 11.03              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker_2      | Timers: 1x ticker                   | 1      | 0      | OK     | 11.04              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker_3      | Timers: 2x callbacks                | 1      | 0      | OK     | 11.04              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-timeout       | Timers: toggle on/off               | 1      | 0      | OK     | 11.25              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-wait_us       | Timers: wait_us                     | 1      | 0      | OK     | 10.05              |
+---------------+---------------+---------------------------------+-------------------------------------+--------+--------+--------+--------------------+
mbedgt: test case results: 1 FAIL / 23 OK / 1 ERROR
mbedgt: completed in 194.37 sec
mbedgt: exited with code 2
```

## mbed test tools detailed list of dependencies

* [Python](https://www.python.org/downloads/). If you do not have Python installed already, we recommend [version 2.7.11](https://www.python.org/downloads/release/python-2711/). You'll need to add the following modules:
  * [Pip](https://pypi.python.org/pypi/pip). Pip comes bundled with some Python versions; run ``$ pip --version`` to see if you already have it.
  * [setuptools](https://pythonhosted.org/an_example_pypi_project/setuptools.html) to install dependencies.
* [yotta](https://github.com/ARMmbed/yotta): used to build tests from the mbed SDK. Please note that **yotta has its own set of dependencies**, listed in the [installation instructions](http://armmbed.github.io/yotta/#installing-on-windows).
* If your OS is Windows, please follow the installation instructions [for the serial port driver](https://developer.mbed.org/handbook/Windows-serial-configuration).
* The mbed OS module ```mbed-drivers```. It is available [on GitHub](https://github.com/ARMmbed/mbed-drivers) but you can use yotta to grab it - we’ll see how later.
* (Optional) The ``cp`` shell command must be available to flash certain boards. It is sometimes available by default, for example on Linux, or you can install the [Git command line tools](https://github.com/github/hub).

To check whether the mbed test tools dependencies exist on your machine:

```
$ pip freeze | grep mbed
mbed-greentea==0.2.6
mbed-host-tests==0.2.4
mbed-ls==0.2.1
```

## Installing Greentea

### Installation from PyPI (Python Package Index)

The ```mbed-greentea``` module is redistributed via PyPI. We recommend you use install it with [application pip](https://pip.pypa.io/en/latest/installing.html#install-pip).

```
$ pip install mbed-greentea --upgrade
```

**Note:** Python 2.7.9 and later (on the Python 2 series), and Python 3.4 and later include pip by default, so you may have pip already.

### Installation from Python sources

To install the mbed test suite, first clone the `greentea` repository:

```
$ git clone https://github.com/ARMmbed/greentea.git
```

Change the directory to the `greentea` directory:

```
$ cd greentea
```

Now you are ready to install `greentea`:

```
$ python setup.py install
```

On Linux, if you have a problem with permissions, use `sudo`:

```
$ sudo python setup.py install
```

To check whether the installation was successful try running the ```mbedgt --help``` command and check that it returns information (you may need to restart your terminal first):

```
$ mbedgt --help
Usage: mbedgt-script.py [options]

This automated test script is used to test mbed SDK 3.0 on mbed-enabled
devices with support from yotta build tool

Options:
  -h, --help            show this help message and exit
```

### Virtual Environments (Python)

You may already recognize that out test tools are mainly written in Python (2.7). If your project / Continuous Integration job is using Python tools and Python packages extensively you may find that installing our test tools may cause Python dependencies collision. To avoid unnecessary hassle and separate packages used by tools and your system you can use virtual environment!

*A Virtual Environment is a tool to keep Python package dependencies required by different projects in separate places, by creating virtual Python environments for them.*

For more details check [Virtual Environments](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

#### How to get and install virtualenv

The simplest way is to just install ```virtualenv``` via ```pip```:
```
$ pip install virtualenv
```

#### Basic Usage

* Create a virtual environment for your project:
```
$ cd my_project
$ virtualenv venv
```

* To begin using the virtual environment (On Windows), it needs to be activated:
```bash
$ venv\Scripts\activate.bat
```

* To begin using the virtual environment (On Linux), it needs to be activated:
```bash
$ source venv/bin/activate
```

* Install packages as usual, for example:
```bash
$ pip install yotta
$ pip install mbed-greentea
  pip ...
```

* If you are done working in the virtual environment (On Windows) for the moment, you can deactivate it:
```
$ venv/script/deactivate.bat
```

* If you are done working in the virtual environment (On Windows) for the moment, you can deactivate it:
```
$ source venv/bin/deactivate
```

#### virtualenv example usage - Windows environment
Setup virtual environment and install all dependencies:
```bash
$ cd my_project
$ virtualenv venv
$ venv/script/activate.bat

$ pip install yotta
$ pip install mbed-greentea
```
Call your test procedures and tools using active environment, for example:
```bash
$ git clone  https://github.com/ARMmbed/mbed-drivers.git
$ cd mbed-drivers
$ yotta target frdm-k64f-gcc
$ yotta build
$ mbedgt -VS
```

Finally deactivate environment and go back to original Python module dependency settings:
```
$ venv/script/deactivate.bat
```

## Environment check

At this point you should have all the dependencies and be ready to build the ```mbed-drivers``` and perform automated testing. Make sure you have installed all of the tools. For example you can list all mbed devices connected to your host computer.
Run command
```
$ mbedls
```
and you'll get:

```
+---------------+----------------------+-------------+-------------+-------------------------------+-----------------+
| platform_name | platform_name_unique | mount_point | serial_port | target_id                     | daplink_version |
+---------------+----------------------+-------------+-------------+-------------------------------+-----------------+
| K64F          | K64F[0]              | E:          | COM201      | 024002265f1b1e5400000a2c2e3ec | 0226            |
+---------------+----------------------+-------------+-------------+-------------------------------+-----------------+
```

## Building the mbed-drivers for yotta target target

You need to build the ```mbed-drivers``` for the target you're testing. We'll use the **Freescale FRDM-K64F** as an example.

Change directories to the mbed sources included in your release files:

```
$ cd mbed-drivers
```

Set your target, for example:

```
$ yotta target frdm-k64f-gcc
```

Then build the ```mbed-drivers``` (you don’t need to specify what you’re building; yotta builds the code in the current directory):

```
$ yotta build
```

# Testing

Start by examining the current configuration using ``mbedgt`` (which itself uses ``mbed-ls``). In this example, a ``` K64F``` board is connected to the host system:

```
$ mbedgt --config
Usage: mbedls-script.py [options]

mbedls-script.py: error: no such option: --config

[master] C:\Work\mbed-drivers> mbedgt --config
mbedgt: checking for yotta target in current directory
        reason: no --target switch set
mbedgt: checking yotta target in current directory
        calling yotta: yotta --plain target
mbedgt: assuming default target as 'frdm-k64f-gcc'
mbedgt: detecting connected mbed-enabled devices...
mbedgt: detected 1 device
        detected 'K64F' -> 'K64F[0]', console at 'COM201', mounted at 'E:', target id '024002265f1b1e54000000000000000000000000a2c2e3ec'
mbedgt: local yotta target search in './yotta_targets' for compatible mbed-target 'k64f'
        inside './yotta_targets\frdm-k64f-gcc' found compatible target 'frdm-k64f-gcc'
mbedgt: processing 'frdm-k64f-gcc' yotta target compatible platforms...
mbedgt: processing 'K64F' platform...
mbedgt: using platform 'K64F' for test:
        target_id_mbed_htm = '024002265f1b1e54000000000000000000000000a2c2e3ec'
        daplink_url = 'http://mbed.org/device/?code=024002265f1b1e54000000000000000000000000a2c2e3ec'
        mount_point = 'E:'
        daplink_version = '0226'
        target_id = '024002265f1b1e54000000000000000000000000a2c2e3ec'
        serial_port = 'COM201'
        target_id_usb_id = '024002265f1b1e54000000000000000000000000a2c2e3ec'
        platform_name = 'K64F'
        platform_name_unique = 'K64F[0]'
        daplink_build = 'Aug 24 2015 17:06:30'
        daplink_git_local_mods = 'Yes'
        daplink_git_commit_sha = '27a236b9fe39c674a703c5c89655fbd26b8e27e1'
        use 0 instances for testing

Example: execute 'mbedgt --target=TARGET_NAME' to start testing for TARGET_NAME target
mbedgt: completed in 1.05 sec
```

There are at least two compatible with yotta Freescale K64F platform targets:
* ```frdm-k64f-gcc``` - Target for Freescale K64F platform compiled with the GCC cross-compiler, see [here](http://yotta.mbed.com/#/target/frdm-k64f-gcc/2.0.0).
* ```frdm-k64f-armcc``` - Target for Freescale K64F platform compiled with the Keil armcc cross-compiler, see [here](http://yotta.mbed.com/#/target/frdm-k64f-armcc/2.0.0).

For simplicity, only the [GCC ARM Embedded](https://launchpad.net/gcc-arm-embedded) compatible targets are described below.

You can invoke ```yotta``` from within ```mbedgt``` (Greentea) to build the targets. In this example:
* ```--target``` option is used to specify the targets that the test suite will interact with.
* The option ```-S``` is used to tell the test suite to *build* sources and tests, but not to *run* the tests.

```
$ mbedgt --target=frdm-k64f-gcc -O
```

You'll get:

```
mbedgt: detecting connected mbed-enabled devices...
mbedgt: detected 1 device
        detected 'K64F' -> 'K64F[0]', console at 'COM201', mounted at 'E:', target id '024002265f1b1e54000000000000000000000000a2c2e3ec'
mbedgt: local yotta target search in './yotta_targets' for compatible mbed-target 'k64f'
        inside './yotta_targets\frdm-k64f-gcc' found compatible target 'frdm-k64f-gcc'
mbedgt: processing 'frdm-k64f-gcc' yotta target compatible platforms...
mbedgt: processing 'K64F' platform...
mbedgt: using platform 'K64F' for test:
        target_id_mbed_htm = '024002265f1b1e54000000000000000000000000a2c2e3ec'
        daplink_url = 'http://mbed.org/device/?code=024002265f1b1e54000000000000000000000000a2c2e3ec'
        mount_point = 'E:'
        daplink_version = '0226'
        target_id = '024002265f1b1e54000000000000000000000000a2c2e3ec'
        serial_port = 'COM201'
        target_id_usb_id = '024002265f1b1e54000000000000000000000000a2c2e3ec'
        platform_name = 'K64F'
        platform_name_unique = 'K64F[0]'
        daplink_build = 'Aug 24 2015 17:06:30'
        daplink_git_local_mods = 'Yes'
        daplink_git_commit_sha = '27a236b9fe39c674a703c5c89655fbd26b8e27e1'
mbedgt: building your sources and tests with yotta...
        calling yotta: yotta --target=frdm-k64f-gcc,* build
info: generate for target: frdm-k64f-gcc 2.0.0 at c:\Work\mbed-drivers\yotta_targets\frdm-k64f-gcc

GCC version is: 4.9.3
-- Configuring done
-- Generating done
-- Build files have been written to: C:/Work/mbed-drivers/build/frdm-k64f-gcc
ninja: no work to do.
mbedgt: yotta build for target 'frdm-k64f-gcc' was successful
        use 0 instances for testing
mbedgt: all tests finished!
mbedgt: completed in 5.92 sec
```

Now that the tests are built, the test suite can be called again to run the tests. From the same directory, invoke ```mbedgt``` again as shown below (this is the same command, but without the -O option):

```
$ mbedgt --target=frdm-k64f-gcc
```
or if you want to be more verbose (use verbose option ```-V```):
```
$ mbedgt -V --target=frdm-k64f-gcc
```

Above command will execute all tests for yotta module you are in, e.g. ```mbed-drivers```.

# Test specification JSON formatted input

Greentea originally only supports yotta artefacts. It assumes it is run inside a yotta module and gathers information from local file system. To make it generic for any other test artefacts we can support a test specification input. This specification can tell information like platform, toolchain, build artefacts path, test binaries, flash methods of test binaries to Greentea.
Test specification is an interface which can be used by any build system or it can be created manually. Test specification interface was added to separate build system from test automation automation (Greentea).

Changes:
* New command line switch `--test-spec` is introduced. It is used to pass test specification file name to Greentea.
* Existing command line switch `-t` together with `--test-spec` switch can be used to select build(s) by name which should be used for test runs. When no test specification is defined switch `-t` / `--target` behaves as usual: you can select yotta targets inside yotta module.

## Test specification formatted

More detailed test specification format will be introduced in near future. In current form test specification is a dictionary with key-value pairs under "builds" entry where key is a build name and value is a dictionary with additional properties describing build itself. Build properties include platform name, toolchain used to compile, interface chip baudrate, and list of test binaries.

## Example of test specification file

In the below example there are two builds defined:
* Build `K64F-ARM` for Freescale `K64F` platform compiled with `ARMCC` compiler and
* build `K64F-GCC` for Freescale `K64F` platform compiled with `GCC ARM` compiler.

```json
{
    "builds": {
        "K64F-ARM": {
            "platform": "K64F",
            "toolchain": "ARM",
            "base_path": "./.build/K64F/ARM",
            "baud_rate": 115200,
            "tests": {
                "mbed-drivers-test-generic_tests":{
                    "binaries":[
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/ARM/mbed-drivers-test-generic_tests.bin"
                        }
                    ]
                },
                "mbed-drivers-test-c_strings":{
                    "binaries":[
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/ARM/mbed-drivers-test-c_strings.bin"
                        }
                    ]
                }
            }
        },
        "K64F-GCC": {
            "platform": "K64F",
            "toolchain": "GCC_ARM",
            "base_path": "./.build/K64F/GCC_ARM",
            "baud_rate": 115200,
            "tests": {
                "mbed-drivers-test-generic_tests":{
                    "binaries":[
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/GCC_ARM/mbed-drivers-test-generic_tests.bin"
                        }
                    ]
                }

            }
        }

    }
}
```

In below examples we will use above test specification file.

### Command line usage

When building your mbed projects with *build system* capable of returning test specification in our format you can directly call Greentea to execute tests or list available tests (`-l` / `--list` switch).

#### Executing all tests

Assuming that `test_spec.json` is in current directory:
```
$ mbedgt -VS
```
will pick up test specification and execute all tests in it.

#### Cherry-pick tests

* We will first list the tests we want to execute:

Assuming that `test_spec.json` is in current directory:
```
$ mbedgt -l
```
```
mbedgt: using 'test_spec.json' from current directory!
mbedgt: available tests for built 'K64F-ARM', location './.build/K64F/ARM'
        test 'mbed-drivers-test-generic_tests'
        test 'mbed-drivers-test-c_strings'
mbedgt: available tests for built 'K64F-GCC', location './.build/K64F/GCC_ARM'
        test 'mbed-drivers-test-generic_tests'
```

* Now we can select test case(s) by name(s) using `-n` switch:

Below command will execute tests with name `mbed-drivers-test-generic_tests` from all builds in build specification:
```
$ mbedgt -V -n mbed-drivers-test-generic_tests
```

Below command will execute tests with name `mbed-drivers-test-generic_tests` only from build `K64F-ARM` in build specification:
```
$ mbedgt -V -n mbed-drivers-test-generic_tests -t K64F-ARM
```

Note: you can use comman '`,`' to separate test names (switch `-n`) and build names (switch `-t`)

#### Cherry-pick group of tests

When using Greentea switch `-n` and putting `*` at the end of test suite name filter will run to filter in all test suite names starting with string before `*`.

* Filter all tests with names starting with 'mbed-drivers-t', e.g.:
```
$ mbedgt -V -n mbed-drivers-t*
```

* Filter all tests with names starting with 'mbed-drivers-t' and test case `tests-mbed_drivers-rtc`
```
$ mbedgt -V -n mbed-drivers-t*,tests-mbed_drivers-rtc
```

# Using Greentea with new targets
When prototyping or developing new port you will find yourself in a situation where your yotta modules are not published (especially targets) and you still want to use Greentea.

## Greentea and yotta targets

Greentea uses the ```yotta search``` command to check that it has proper support for your board before calling tests.
For example you can check compatible the yotta registry by calling:
```
$ yotta --plain search -k mbed-target:k64f target
frdm-k64f-gcc 0.2.0:
    Official mbed build target for the mbed frdm-k64f development board.
    mbed-target:k64f, mbed-official, k64f, frdm-k64f, gcc
frdm-k64f-armcc 0.1.4:
    Official mbed build target for the mbed frdm-k64f development board, using the armcc toolchain.
    mbed-target:k64f, mbed-official, k64f, frdm-k64f, armcc

additional results from https://yotta-private.herokuapp.com:
```
Here two targets are officially compatible with the ```K64F``` target: ``` frdm-k64f-gcc ```` and ``` frdm-k64f-armcc ```. They are both the same board, but each target uses a different toolchain: gcc and armcc.

If you’re working with a target that isn’t officially supported, you’ll have to follow the steps below.

## Prototyping support

Greentea by default will only allow tests for boards officially supported by a yotta target. This contradicts prototyping and porting workflow. Your workflow may include use of [```yotta link```](http://yottadocs.mbed.com/reference/commands.html#yotta-link) and [```yotta link-target```](http://yottadocs.mbed.com/reference/commands.html#yotta-link-target) commands.

To support these workflows, we’ve created a command line switch ```--map-target``` was added. It adds an extra mapping between mbed board names and supported yotta targets.

For example we can add a local yotta target ```frdm-k64f-iar```. This is a ```K64F``` using the compiler ``IAR```:
```
$ mbedgt --map-target K64F:frdm-k64f-iar
```
Note:
* This command will only work locally. Use it while you are porting / protoyping.
* When officially releasing your yotta targets please add correct yotta search bindings the ```keywords``` section of ```target.json```'.

See example of official yotta target's [target.json]( https://github.com/ARMmbed/target-frdm-k64f-gcc/blob/master/target.json):
```json
"keywords": [
    "mbed-target:k64f",
    "mbed-official",
    "k64f",
    "frdm-k64f",
    "gcc"
],
```
Note that the value ```"mbed-target:k64f"``` is added to mark that this yotta target supports the ```K64F``` board.

### How to add board-target bindings for Greentea

In your yotta target ```target.json``` file, in the section ```keywords```, add the value: ```mbed-target:<PLATFORM>``` where ```<PLATFORM>``` is the platform’s name in lowercase.

* Check the platform’s name using the ```mbedls``` command:
```
$ mbedls
+--------------+ ...
|platform_name | ...
+--------------+ ...
|K64F          | ...
|LPC1768       | ...
+--------------+ ...
```

* Search for ```mbed-target``` keyword values in yotta registry from command line:

```bash
$ $ yotta --plain search -k mbed-target:k64f target
frdm-k64f-gcc 2.0.0:
    Official mbed build target for the mbed frdm-k64f development board.
    mbed-target:k64f, mbed-official, mbed, k64f, frdm-k64f, gcc
frdm-k64f-armcc 2.0.0:
    Official mbed build target for the mbed frdm-k64f development board, using the armcc toolchain.
    mbed-target:k64f, mbed-official, mbed, k64f, frdm-k64f, armcc
my-target 0.1.4:
    my target
target-onsemi-ncs36510-gcc 0.1.0:
    Official mbed build target for .
    mbed-official, mbed, onsemi, ncs36510, gcc
test-target-dep 0.0.2:
    Test Target Test Dependencies
    autopulated

additional results from https://yotta-private.herokuapp.com:
```

### Prototyping or porting - sample workflow

**Note:** This is an example workflow; you may need to add or remove steps for your own workflow.

This example creates a new mbed yotta target, then runs ```mbed-drivers``` tests on it to check that it was ported correctly.

* Clone the [```mbed-drivers```](https://github.com/ARMmbed/mbed-drivers) repository
* Create your new target locally (have a look at [```frdm-k64f-gcc```](https://github.com/ARMmbed/target-frdm-k64f-gcc) as an example, or read the [```target docs here```](http://yottadocs.mbed.com/tutorial/targets.html))
* Use [yotta link-target](http://yottadocs.mbed.com/reference/commands.html#yotta-link-target) to link your target into mbed-drivers
* Create your HAL and CMSIS port modules
* Use [```yotta link```](http://yottadocs.mbed.com/reference/commands.html#yotta-link) to link these to ```mbed-drivers```
* Download the git version of mbed HAL, add your new hal and CMSIS modules as target-dependencies
* Use yotta link to link ```mbed-hal``` to ```mbed-drivers```
* In ```mbed-drivers```: set your target, compile and test!
* Edit your HAL modules until things work, committing and pushing to your source control as you go
* When your modules and targets are ready for public consumption, open a Pull request on mbed-hal with your dependency addition, and `yotta publish` your target and module(s)

Note that we're now using [config.html](http://yottadocs.mbed.com/reference/config.html) for pin definitions. mbed-hal has a script that processes config definitions into pin definitions, see frdm-k64f targets for an example of how to define these: [target.json](https://github.com/ARMmbed/target-frdm-k64f-gcc/blob/master/target.json#L38))

# Selecting boards for test running

You and tell Greentea which board it can use for test. To do so prepare list of allowed Target IDs and specify this list using ```--use-tids``` command line switch.  The list should be comma separated.
```
$ mbedgt --use-tids 02400203C3423E603EBEC3D8,024002031E031E6AE3FFE3D2
```
Where ```02400203C3423E603EBEC3D8``` and ```024002031E031E6AE3FFE3D2``` might be target IDs of devices available in your system.
Note: You can check target IDs of the connected devices using ```mbedls``` command:
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

## Option --use-tids example
We want to run two instances of Greentea and perform test sessions that won’t interfere with each other using two ```K64F``` boards:
My resources (2 x ```K64F``` boards):
```
$ mbedls
+--------------+---------------------+------------+------------+-------------------------+
|platform_name |platform_name_unique |mount_point |serial_port |target_id                |
+--------------+---------------------+------------+------------+-------------------------+
|K64F          |K64F[0]              |E:          |COM160      |024002031E031E6AE3FFE3D2 |
|K64F          |K64F[1]              |F:          |COM162      |02400203C3423E603EBEC3D8 |
+--------------+---------------------+------------+------------+-------------------------+
```

We can use two consoles to call ```mbedgt```. Each one will specify one target ID, and will therefore run tests only on that target:

Console 1:
```
$ cd <yotta module X>
$ mbedgt –use-tids 024002031E031E6AE3FFE3D2
```
Console 2:
```
$ cd <yotta module Y>
$ mbedgt –use-tids 02400203C3423E603EBEC3D8
```
The two instances of Greentea are called at the same time, but since we provide two mutually exclusive subsets of allowed target IDs with switch ```--use-tids``` the two instances will not collide and will not try to access the same ```K64F``` board when testing.


# Additional features

## Dynamic host test loader

* This feature allows users to point ```greentea``` and (indirectly ```mbedhtrun```) to arbitrary directory (switch ```-e <dir>``` containing new/proprietary host test scripts. Host tests script files are enumerated in ```<dir>``` and registered so they can be used with local module test cases.
* Not all host tests can be stored with ```mbedhtrun``` package. Some of them may and will be only used locally, for prototyping. Some host tests may just be very module dependent and should not be stored with ``mbedhtrun```.
* In many cases users will add host tests to their yotta modules preferably under ```/test/host_tests/```module directory.
* **Note**: Directory ytmodule```/test/host_tests``` will be default local host test location used by test tools such as ```greentea```.
* This feature allows ```mbedhtrun``` to load and register additional host test scripts from given directory.
* Feature implementation is [here](https://github.com/ARMmbed/greentea/pull/33)

## yotta config parse

* Greentea reads ```yotta_config.json``` file to get information regarding current yotta module configuration.
* Currently ```yotta_config::mbed-os::stdio::default-baud``` setting is read to determine default (interface chip) serial port baudrate. Note that this serial port is usually hooked to mbed's ```stdio```.
* This feature changes dafault yotta connfiguration baudrate (default-baud) to 115200. All test tool follow this change.
* Feature implementation is [here](https://github.com/ARMmbed/greentea/pull/41)

## Local yotta targets scan for mbed-target keywords

* ```yotta search``` command was used to check for compatibility between connected mbed devices and specified (available) yotta targets.
* New functionality uses locally stored yotta targets (```mymodule/yotta_targets``` directory) to do so and allows user to add yotta registry results with new command line switch ```--yotta-registry```.
* This method is much faster than yotta registry queries and allows users to work and test off-line.
* Feature implementation is [here](https://github.com/ARMmbed/greentea/pull/42)

# Common Issues

* Issue: In this release there are known issues related to Virtual Machine support.
  * Note: We are not planning to support VMs soon. If you are using our testing tools on VM and experiencing e.g. ``` IOERR_SERIAL``` errors you should probably switch to native OS.
* Issue: In this release there are known issues related to Linux and MacOS serial port handling during test.
  * Solution: Please use latest interface chip firmware for your mbed boards.
* Issue: Some boards show up as 'unknown'.
  * Solution: We will add them in coming releases.
* Issue: Not all mbed boards have targets mapped to them.
  * Solution: More mbed boards will be added in coming releases.

## Uninstalling Greentea

You can uninstall the test suite package using ```pip```. List installed packages and filter for the test suite's package name:

```bash
$ pip freeze | grep mbed-greentea
mbed-greentea==0.0.5
```

Uninstall the test suite package:

```bash
$ pip uninstall mbed-greentea
Uninstalling mbed-greentea:
  c:\python27\lib\site-packages\greentea-0.0.5-py2.7.egg
  c:\python27\scripts\mbedgt-script.py
  c:\python27\scripts\mbedgt.exe
  c:\python27\scripts\mbedgt.exe.manifest
Proceed (y/n)? Y
  Successfully uninstalled mbed-greentea
```

# Commissioning mbed platforms

Please check [Configure mbed-enabled device to work with your host](https://github.com/ARMmbed/mbed-ls#configure-mbed-enabled-device-to-work-with-your-host) if you have problems with mbed device mounting / serial port installation.
