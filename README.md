[![Circle CI](https://circleci.com/gh/ARMmbed/greentea.svg?style=svg)](https://circleci.com/gh/ARMmbed/greentea)

# Table of contents

* [Introduction](#introduction)
* [Supported operating systems](#supported-operating-systems)
  * [Virtual Environments (Python)](#virtual-environments-python)
    * [How to get and install](#how-to-get-and-install)
    * [Basic Usage](#basic-usage)
    * [Basic usage - Windows example](#basic-usage---windows-example)
* [Getting started](#getting-started)
  * [End to end example](#end-to-end-example)
  * [Dependencies](#dependencies)
  * [Installing Greentea](#installing-greentea)
    * [Installation from PyPI (Python Package Index)](#installation-from-pypi-python-package-index)
    * [Installation from Python sources](#installation-from-python-sources)
  * [Environment check](#environment-check)
  * [Building the mbed-drivers for the target](#building-the-mbed-drivers-for-the-target)
* [Testing](#testing)
* [Using Greentea with new targets](#using-greentea-with-new-targets)
  * [Greentea and yotta targets](#greentea-and-yotta-targets)
  * [Prototyping support](#prototyping-support)
    * [How to add board-target bindings for Greentea](#how-to-add-board-target-bindings-for-greentea)
    * [Prototyping or porting sample workflow](#prototyping-or-porting-sample-workflow)
* [Selecting boards for test running](#selecting-boards-for-test-running)
  * [Switch --use-tids example](#switch---use-tids-example)
* [Digesting test output](#digesting-test-output)
  * [Example 1 - digest the default mbed host test runner](#example-1---digest-the-default-mbed-host-test-runner)
  * [Example 2 - digest directly from file](#example-2---digest-directly-from-file)
  * [Example 3 - pipe test.txt file content (as in example 2)](#example-3---pipe-testtxt-file-content-as-in-example-2)
* [Additional features](#additional-features)
  * [Dynamic host test loader](#dynamic-host-test-loader)
  * [yotta config parse](#yotta-config-parse)
  * [Local yotta targets scan for mbed-target keywords](#local-yotta-targets-scan-for-mbed-target-keywords)
* [Common Issues](#common-issues)
  * [Uninstalling Greentea](#uninstalling-greentea)
* [Commissioning mbed platforms (Linux)](#commissioning-mbed-platforms-linux)

# Introduction

Hello and welcome to the mbed SDK test suite, codename *Greentea*. The test suite is a collection of tools that enable automated testing on mbed boards.

In its current configuration, the mbed test suite can automatically detect most of the popular mbed-enabled boards connected to the host over USB. The test suite uses the ```mbed-ls``` module to check for connected devices. A separate module called ```mbed-host-tests``` is used to flash and supervise each board's test. This decoupling allows us to make better software and maintain each of the functionalities as a separate domain.

Additional documentation:
* [Quickstart document](https://github.com/ARMmbed/greentea/blob/master/docs/QUICKSTART.md)
* Things you need to know [when you contribute](https://github.com/ARMmbed/greentea/blob/master/docs/CONTRIBUTING.md) to open source mbed test tools repositories.

# Supported operating systems

* Windows
* Linux (experimental)
* OS X 10.10 (experimental)

## Virtual Environments (Python)
You may already recognize that out test tools are mainly written in Python (2.7).
If your project / CI job etc. is using Python tools and Python packages extensively you may find that installing our test tools may cause Python dependencies collision.
To avoid unnecessary hassle and separate packages used by tools and your system you can use virtual environment!

*A Virtual Environment is a tool to keep Python package dependencies required by different projects in separate places, by creating virtual Python environments for them.*

For more details check [Virtual Environments](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

### How to get and install
The simplest way is to just install ```virtualenv``` via ```pip```:
```
$ pip install virtualenv
```

### Basic Usage
* Create a virtual environment for your project:
```
$ cd my_project
$ virtualenv venv
```

* To begin using the virtual environment (On Windows), it needs to be activated:
```
$ venv\Scripts\activate.bat
```

* To begin using the virtual environment (On Linux), it needs to be activated:
```
$ source venv/bin/activate
```

* Install packages as usual, for example:
```
$ pip install yotta
$ pip install greentea
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

### Basic usage - Windows example
Setup virtual environment and install all dependencies:
```
$ cd my_project
$ virtualenv venv
$ venv/script/activate.bat

$ pip install yotta
$ pip install greentea
```

Call your test procedures and tools using active environment, for example:
```
$ cd yotta_module/
$ mbedgt -V t frdom-k64f-gcc
```

Finally deactivate environment and go back to original Python module dependency settings:

```
$ venv/script/deactivate.bat
```

# Getting started

To use the mbed test suite you must:

* Install the dependencies.
* Download and install the mbed test suite.
* Build the mbed project sources.

## End to end example
This end to end example shows how to install and use Greentea with an example mbed repository.
Example will assume that you:
* Have one mbed board connected to your PC over USB. In our case it will be one Freescale [```K64F```](https://developer.mbed.org/platforms/FRDM-K64F/) board.
* Installed [GNU toolchain for ARM Cortex-M](https://launchpad.net/gcc-arm-embedded).
* Installed [Git](https://git-scm.com/downloads)
* Installed [Python 2.7](https://www.python.org/download/releases/2.7/).

Install [```yotta```](https://github.com/ARMmbed/yotta):
```
$ pip install yotta --upgrade
```
Installing Greentea tools:
```
$ pip install mbed-greentea --upgrade
```
Create a local clone of the [```mbed-drivers```](https://github.com/ARMmbed/mbed-drivers) repository.
```
$ cd some_dir
$ git clone https://github.com/ARMmbed/mbed-drivers.git
$ cd mbed-drivers
```
Make sure your board is compatible with ```K64F``` yotta targets:
```
$ yotta --plain search -k mbed-target:k64f target --short
frdm-k64f-gcc 0.2.0: Official mbed build target for the mbed frdm-k64f development board.
frdm-k64f-armcc 0.1.4: Official mbed build target for the mbed frdm-k64f development board, using the armcc toolchain.

additional results from https://yotta-private.herokuapp.com:
```
Set the yotta build target to ```frdm-k64f-gcc```:
```
$ yotta target frdm-k64f-gcc
```
Build the ```mbed-drivers``` module with yotta (note that Greentea can do this for you also automatically):
```
$ yotta build
```
List the built test cases:
```
$ mbedgt --list
mbedgt: available tests for built targets, location '/home/some_dir/'
        target 'frdm-k64f-gcc':
        test 'mbed-drivers-test-serial_interrupt'
        test 'mbed-drivers-test-blinky'
        test 'mbed-drivers-test-div'
...
        test 'mbed-drivers-test-sleep_timeout'
        test 'mbed-drivers-test-ticker_3'
        test 'mbed-drivers-test-detect'
```
And finally - test (```-V``` is used to activate test case verbose mode):
```
$ mbedgt -V

mbedgt: checking for yotta target in current directory
        reason: no --target switch set
mbedgt: checking yotta target in current directory
        calling yotta: yotta --plain target
mbedgt: assuming default target as 'frdm-k64f-gcc'
mbedgt: detecting connected mbed-enabled devices...
mbedgt: detected 3 devices
        detected 'K64F' -> 'K64F[0]', console at 'COM160', mounted at 'E:', target id '024002031E031E6AE3FFE3D2'
...
mbedgt: running 20 tests for target 'frdm-k64f-gcc' and platform 'K64F'
        running host test...
        test 'mbed-drivers-test-serial_interrupt' .............................................. OK in 6.16 sec
        running host test...
        test 'mbed-drivers-test-blinky' ........................................................ OK in 4.42 sec
        running host test...
        test 'mbed-drivers-test-div' ........................................................... OK in 1.41 sec
...
mbedgt: test report:
+---------------+---------------+------------------------------------+--------+--------------------+-------------+
| target        | platform_name | test                               | result | elapsed_time (sec) | copy_method |
+---------------+---------------+------------------------------------+--------+--------------------+-------------+
| frdm-k64f-gcc | K64F          | mbed-drivers-test-serial_interrupt | OK     | 6.16               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-blinky           | OK     | 4.42               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-div              | OK     | 1.41               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-dev_null         | OK     | 3.5                | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stdio            | OK     | 0.74               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-sleep_timeout    | OK     | 3.38               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker           | OK     | 11.38              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-rtc              | OK     | 4.55               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-cstring          | FAIL   | 1.39               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-cpp              | OK     | 1.34               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-timeout          | OK     | 11.55              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-basic            | OK     | 1.37               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker_3         | OK     | 11.38              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker_2         | OK     | 11.38              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-heap_and_stack   | OK     | 1.39               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-hello            | OK     | 0.37               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-time_us          | OK     | 11.37              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stl              | OK     | 1.36               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-echo             | OK     | 6.33               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-detect           | OK     | 0.47               | shell       |
+---------------+---------------+------------------------------------+--------+--------------------+-------------+

Result: 1 FAIL / 19 OK
Completed in 269.49 sec
```

## Dependencies

Please install the following:

* [Python](https://www.python.org/downloads/). If you do not have Python installed already, we recommend [version 2.7.9](https://www.python.org/downloads/release/python-279/). You'll need to add the following modules:

	* [Pip](https://pypi.python.org/pypi/pip). Pip comes bundled with some Python versions; run ``$ pip --version`` to see if you already have it.

	* [setuptools](https://pythonhosted.org/an_example_pypi_project/setuptools.html) to install dependencies.

	* cryptography (install using ``pip``).

	* hgapi (install using ``pip``).

	* colorama (install using ``pip``).

	* PyGithub (install using ``pip``).

	* semantic_version==2.4.1 (install using ``pip``) - note that it requires [Microsoft Visual C++ 9.0](http://www.microsoft.com/en-gb/download/details.aspx?id=44266).

	* project-generator==0.5.7 (install using ``pip``).

	* pyOCD (install using ``pip``).

* The ``cp`` shell command must be available to flash certain boards. It is sometimes available by default, for example on Linux, or you can install the [Git command line tools](https://github.com/github/hub).

* [Grep](http://gnuwin32.sourceforge.net/packages/grep.htm) and [cat](http://gnuwin32.sourceforge.net/packages/coreutils.htm).

* [yotta](https://github.com/ARMmbed/yotta): used to build tests from the mbed SDK. Please note that **yotta has its own set of dependencies**, listed in the [installation instructions](http://armmbed.github.io/yotta/#installing-on-windows).

* If your OS is Windows, please follow the installation instructions [for the serial port driver](https://developer.mbed.org/handbook/Windows-serial-configuration).

* The mbed OS module ```mbed-drivers```. It is available [on GitHub](https://github.com/ARMmbed/mbed-drivers) but you can use yotta to grab it - we’ll see how later.

* mbed-ls: installation instructions can be found [in the repository](https://github.com/ARMmbed/mbed-ls#installation-from-python-sources).

* mbed-host-tests: installation instructions can be found [in the respository](https://github.com/ARMmbed/mbed-host-tests#installation-from-python-sources).

To check whether the mbed dependencies exist on your machine:

```
pip freeze | grep mbed
mbed-host-tests==0.1.4
mbed-ls==0.1.5
```

## Installing Greentea
### Installation from PyPI (Python Package Index)

The ```mbed-greentea``` module is redistributed via PyPI. We recommend you use install it with [application pip](https://pip.pypa.io/en/latest/installing.html#install-pip).

```
$ pip install mbed-greentea
```

**Note:** Python 2.7.9 and later (on the Python 2 series), and Python 3.4 and later include pip by default, so you may have pip already.

### Installation from Python sources
To install the mbed test suite, first clone the `greentea` repository:

```
$ git clone <link-to-greentea-repo>
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
deviecs with support from yotta build tool

Options:
  -h, --help            show this help message and exit
.
.
```

## Environment check

At this point you should have all the dependencies and be ready to build the ```mbed-drivers``` and perform automated testing.

Make sure you have installed all of the tools. For example you can list all mbed devices connected to your host computer.
Run command
```
$ mbedls
```
and you'll get:

```
+---------------------+-------------------+-------------------+--------------------------------+
|platform_name        |mount_point        |serial_port        |target_id                       |
+---------------------+-------------------+-------------------+--------------------------------+
|K64F                 |E:                 |COM61              |02400203D94B0E7724B7F3CF        |
+---------------------+-------------------+-------------------+--------------------------------+
```

## Building the mbed-drivers for the target

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
```

You'll see:

```
mbed-ls: detecting connected mbed-enabled devices...
mbed-ls: detected K64F, console at: COM61, mounted at: E:
        got yotta target 'frdm-k64f-gcc'
        got yotta target 'frdm-k64f-armcc'
```

```mbedgt``` proposed a few supported yotta targets:

* ```frdm-k64f-gcc``` - Freescale K64F platform compiled with the GCC cross-compiler.
* ```frdm-k64f-armcc``` - Freescale K64F platform compiled with the Keil armcc cross-compiler.

For simplicity, only the GCC targets are described below.

You can invoke yotta from the test suite to build the targets. In this example:

* ```--target``` is used to specify the targets that the test suite will interact with.
* The option ```-O``` is used to tell the test suite to *build* sources and tests, but not to *run* the tests.

```
$ mbedgt --target=frdm-k64f-gcc -O
```

You'll get:

```
mbed-ls: detecting connected mbed-enabled devices...
mbed-ls: detected K64F, console at: COM61, mounted at: E:
        got yotta target 'frdm-k64f-gcc'
mbed-ls: calling yotta to build your sources and tests
warning: uvisor-lib has invalid module.json:
info: generate for target: frdm-k64f-gcc 0.0.10 at c:\temp\xxx\mbed-sdk-private\yotta_targets\frdm-k64f-gcc
mbedOS.cmake included
GCC-C.cmake included
mbedOS-GNU-C.cmake included
GCC-GXX.cmake included
mbedOS-GNU-CXX.cmake included
GCC version is: 4.8.4
GNU-ASM.cmake included
GNU-ASM.cmake included
-- Configuring done
-- Generating done
-- Build files have been written to: C:/temp/xxx/mbed-sdk-private/build/frdm-k64f-gcc
ninja: no work to do.
```

Now that the tests are built, the test suite can be called again to run the tests. From the same directory, invoke ```mbedgt``` again as shown below (this is the same command, but without the -O option):

```
$ mbedgt --target=frdm-k64f-gcc
```
or if you want to be more verbose:
```
$ mbedgt -V --target=frdm-k64f-gcc
```

You'll see:

```
mbed-ls: detecting connected mbed-enabled devices...
mbed-ls: detected K64F, console at: COM61, mounted at: E:
        got yotta target 'frdm-k64f-gcc'
mbed-ls: calling yotta to build your sources and tests
info: generate for target: frdm-k64f-gcc 0.0.10 at c:\temp\xxx\mbed-sdk-private\yotta_targets\frdm-k64f-gcc
mbedOS.cmake included
GCC-C.cmake included
mbedOS-GNU-C.cmake included
GCC-GXX.cmake included
mbedOS-GNU-CXX.cmake included
GCC version is: 4.8.4
GNU-ASM.cmake included
GNU-ASM.cmake included
-- Configuring done
-- Generating done
-- Build files have been written to: C:/temp/xxx/mbed-sdk-private/build/frdm-k64f-gcc
ninja: no work to do.
mbedgt: running tests...
        test 'mbed-test-dev_null' .................................................... OK
        test 'mbed-test-cpp' ......................................................... OK
        test 'mbed-test-time_us' ..................................................... OK
        test 'mbed-test-ticker' ...................................................... OK
        test 'mbed-test-div' ......................................................... OK
        test 'mbed-test-detect' ...................................................... SKIPPED
        test 'mbed-test-call_before_main' ............................................ OK
        test 'mbed-test-basic' ....................................................... OK
        test 'mbed-test-stdio' ....................................................... OK
        test 'mbed-test-ticker_3' .................................................... OK
        test 'mbed-test-ticker_2' .................................................... OK
        test 'mbed-test-timeout' ..................................................... OK
        test 'mbed-test-rtc' ......................................................... OK
        test 'mbed-test-echo' ........................................................ OK
        test 'mbed-test-hello' ....................................................... OK
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
...
"keywords": [
    "mbed-target:k64f",
    "mbed-official",
    "k64f",
    "frdm-k64f",
    "gcc"
],
...
```
Note that the value ```"mbed-target:k64f"``` is added to mark that this yotta target supports the ```K64F``` board.

### How to add board-target bindings for Greentea
In your yotta target ```target.json``` file, in the section ```keywords```, add the value: ```mbed-target:<PLATFORM>``` where ```<PLATFORM>``` is the platform’s name in lowercase.

You can check the platform’s name using the ```mbedls``` command:
```
$ mbedls
+--------------+ ...
|platform_name | ...
+--------------+ ...
|K64F          | ...
|LPC1768       | ...
+--------------+ ...
```
### Prototyping or porting sample workflow

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

## Switch --use-tids example
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

# Digesting test output

We've added a feature for digesting input, which is activated with the ```--digest``` command line switch. Now you can pipe your proprietary test runner’s console output to the test suite or just ```cat``` a file with the test runner’s console output. You can also specify a file name that will be digested as the test runner's console input.

This option allows you to write your own automation where you execute the test runner or just feed the test suite with the test runner’s console output. The test suite parses the console output to determine whether it indicates success or failure, then returns that status to the test environment.

**Note:**

* ```--digest=stdin``` will force ```stdin``` to be the default test suite input.

* ```--digest=filename.txt``` will force ```filename.txt``` file content to be the default test suite input.

The examples below demonstrate the use of the ```--digest``` option. Assume that you have written a test runner in ```bash``` shell scripting, or just collected a bunch of test results in a database and the test console output is available.

To get the mbed test suite's predefined test results, you must scan the console output from the tests.

**Note:** test suite results and tags are encoded between double curly braces. For example, a typical success code looks like this: ```{{success}}{{end}}```.

## Example 1 - digest the default mbed host test runner

You can run mbed host tests with the ```mbed-host-tests``` module, using ```mbedhtrun``` to evaluate the existing test cases' test results (test results are returned to the environment as ```mbedgt``` return codes; the success code is ```0```).

Run:

**Note:**  You may need to change "E" to the correct mount point and "COM61" to the correct serial port mapping for your system. Run the ``mbedls`` command to see the correct values.

```
$ mbedhtrun -d E: -f ".\build\frdm-k64f-gcc\test\mbed-drivers-test-hello.bin" -p COM61 -C 4 -c default -m K64F | mbedgt --digest=stdin -V
```

And you'll get:

```
MBED: Instrumentation: "COM61" and disk: "E:"
HOST: Copy image onto target...
HOST: Initialize serial port...
HOST: Reset target...
HOST: Property 'timeout' = '5'
HOST: Property 'host_test_name' = 'hello_auto'
HOST: Property 'description' = 'Hello World'
HOST: Property 'test_id' = 'MBED_10'
HOST: Start test...
Read 13 bytes:
Hello World

{{success}}
{{end}}
```

```
$ echo error level is %ERRORLEVEL%
error level is 0
```

Note: the test suite detected strings ```{{success}}``` and ```{{end}}``` and concluded that the test result was a success.

## Example 2 - digest directly from file

Create file ```test.txt``` with the below contents.  Make sure the file ends with a newline.
```
MBED: Instrumentation: "COM61" and disk: "E:"
HOST: Copy image onto target...
HOST: Initialize serial port...
HOST: Reset target...
HOST: Property 'timeout' = '5'
HOST: Property 'host_test_name' = 'hello_auto'
HOST: Property 'description' = 'Hello World'
HOST: Property 'test_id' = 'MBED_10'
HOST: Start test...
Read 13 bytes:
Hello World

{{ioerr_disk}}
{{end}}
```

Run the ```cat``` command and verify the contents contents above are printed:
```
$ cat test.txt
```


And scan for error codes inside the file:

```
$ mbedgt --digest=./test.txt
```
```
$ echo error level is %ERRORLEVEL%
error level is 5
```
Note: error level ```5``` stands for ```TEST_RESULT_IOERR_DISK```.

## Example 3 - pipe test.txt file content (as in example 2)

```
$ cat test.txt | mbedgt --digest=stdin
```
```
$ echo error level is %ERRORLEVEL%
error level is 5
```

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

```
$ pip freeze | grep mbed-greentea
mbed-greentea==0.0.5
```

Uninstall the test suite package:

```
$ pip uninstall mbed-greentea
Uninstalling mbed-greentea:
  c:\python27\lib\site-packages\greentea-0.0.5-py2.7.egg
  c:\python27\scripts\mbedgt-script.py
  c:\python27\scripts\mbedgt.exe
  c:\python27\scripts\mbedgt.exe.manifest
Proceed (y/n)? Y
  Successfully uninstalled mbed-greentea
```

# Commissioning mbed platforms (Linux)
On Ubuntu/Linux target serial device nodes are created with root permissions by default. Forcing user to run mbedgt as root.
Create a udev rules file to change permission of the device nodes when they are created.

```sh
$ vi /etc/udev/rules.d/10-mbed-platforms.rules
```

```sh
SUBSYSTEMS=="usb", ATTRS{idVendor}=="<target Vendor Id>", ATTRS{idProduct}=="<target Product Id>", MODE:="0666"
```

Create a line for each type of platform based on their vendor and platform Ids. With this change mbed devices can be used with any user account.
