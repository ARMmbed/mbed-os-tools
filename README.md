# Introduction

Hello and welcome to the mbed SDK test suite, codename *Greentea*. The test suite is a collection of tools that enable automated testing on mbed platforms.

In its current configuration, the mbed test suite can automatically detect most of the popular mbed-enabled platforms connected to the host via the USB interface. The test suite uses the ```mbed-ls``` module to check for connected devices. A separate module called ```mbed-host-tests``` is used to flash and supervise each platform's test. This decoupling allows us to make better software and maintain each of the functionalities as a separate domain.

# Supported Targets

Operating systems:

* Windows.

mbed platforms:

* [FRDM-K64F](http://developer.mbed.org/platforms/FRDM-K64F/).
* [NUCLEO_F401RE](http://developer.mbed.org/platforms/ST-Nucleo-F401RE/).

yotta targets:

* ```frdm-k64f-gcc```.
* ```frdm-k64f-armcc```.
* ```st-nucleo-f401re-gcc```.

**Note:** More platforms and yotta targets will be added. For most platforms and targets, only the meta-data must be updated.

# Getting Started

To use the mbed test suite you must:

* Install the dependencies.
* Download and install the mbed test suite.
* Build the mbed SDK sources.

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

* The ``cp`` shell command must be available to flash certain boards, such as the Nucleo F401RE. It is sometimes available by default, for example on Linux, or you can install the [Git command line tools](https://github.com/github/hub).

* [Grep](http://gnuwin32.sourceforge.net/packages/grep.htm).

* [yotta](https://github.com/ARMmbed/yotta): used to build tests from the mbed SDK. Please note that **yotta has its own set of dependencies**, listed in the [installation instructions](http://armmbed.github.io/yotta/#installing-on-windows).

* If your OS is Windows, please follow the installation instructions [for the serial port driver](https://developer.mbed.org/handbook/Windows-serial-configuration).

* The mbed SDK sources. These are provided in the release sources under the **libraries/mbed-sdk** directory.

* mbed-ls: installation instructions can be found [in the repository](https://github.com/ARMmbed/mbed-ls#installation-from-python-sources).

* mbed-host-tests: installation instructions can be found [in the respository](https://github.com/ARMmbed/mbed-host-tests#installation-from-python-sources).

To check whether the mbed dependencies exist on your machine:

```
pip freeze | grep mbed
mbed-host-tests==0.1.4
mbed-ls==0.1.5
```

## Installing Greentea

To install the mbed test suite go to the Tools folder in your release and run the setup.py script with the install option.

```
$ cd tools/mbed-greentea
$ python setup.py install
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

## Environment Pre-Check

At this point you should have all the dependencies and be ready to build the mbed SDK and perform automated testing.

Make sure you have installed all of the tools. For example you can list all mbed devices connected to your host computer. Tun ``$ mbedls`` and you'll get:

```
+---------------------+-------------------+-------------------+--------------------------------+
|platform_name        |mount_point        |serial_port        |target_id                       |
+---------------------+-------------------+-------------------+--------------------------------+
|K64F                 |E:                 |COM61              |02400203D94B0E7724B7F3CF        |
|NUCLEO_F401RE        |F:                 |COM52              |07200200073E650A385BF317        |
+---------------------+-------------------+-------------------+--------------------------------+
```

## Building the SDK for the Target

You need to build the SDK for the target you're testing. Two targets are currently supported: **Freescale FRDM-K64F** and **ST Nucleo-F401RE**.

Change directories to the mbed sources included in your release files:

```
$ cd libraries/mbed-sdk
```

Set your target, for example:

```yotta target st-nucleo-f401re-gcc```

Then build the SDK:

```yotta build```

# Testing

Start by examining the current configuration using ``mbedgt`` (which itself uses ``mbed-ls``). In this example, two boards are connected to the host system: ``` K64F```, ```NUCLEO_F401RE ```:

```
$ mbedgt --config
```

You'll see:

```
mbed-ls: detecting connected mbed-enabled devices...
mbed-ls: detected K64F, console at: COM61, mounted at: E:
        got yotta target 'frdm-k64f-gcc'
        got yotta target 'frdm-k64f-armcc'
mbed-ls: detected NUCLEO_F401RE, console at: COM52, mounted at: F:
        got yotta target 'st-nucleo-f401re-gcc'
```

```mbedgt``` proposed a few supported yotta targets:

* ```frdm-k64f-gcc``` - Freescale K64F platform compiled with the GCC cross-compiler.
* ```frdm-k64f-armcc``` - Freescale K64F platform compiled with the Keil armcc cross-compiler.
* ```st-nucleo-f401re-gcc``` - STMicro Nucleo F401RE platform compiled with the GCC cross-compiler.

For simplicity, only the GCC targets are described below.  

You can invoke yotta from the test suite to build the targets. In this example:

* ```--target``` is used to specify the targets that the test suite will interact with.  
* The option ```-O``` is used to tell the test suite to *build* sources and tests, but not to *run* the tests.

```
$ mbedgt --target=frdm-k64f-gcc,st-nucleo-f401re-gcc -O
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
        got yotta target 'frdm-k64f-armcc'
mbed-ls: detected NUCLEO_F401RE, console at: COM52, mounted at: F:
        got yotta target 'st-nucleo-f401re-gcc'
mbed-ls: calling yotta to build your sources and tests
info: generate for target: st-nucleo-f401re-gcc 0.0.5 at c:\temp\xxx\mbed-sdk-private\yotta_targets\st-nucleo-f401re-gcc
mbedOS.cmake included
GCC-C.cmake included
mbedOS-GNU-C.cmake included
GCC-GXX.cmake included
mbedOS-GNU-CXX.cmake included
GCC version is: 4.8.4
GNU-ASM.cmake included
-- Configuring done
-- Generating done
-- Build files have been written to: C:/temp/xxx/mbed-sdk-private/build/st-nucleo-f401re-gcc
ninja: no work to do.
```

Now that the tests are built, the test suite can be called again to run the tests. From the same director, invoke ```mbedgt``` again as shown below (this is the same command, but without the -O option):

```
$ mbedgt --target=frdm-k64f-gcc,st-nucleo-f401re-gcc
```

You'll see

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
        got yotta target 'frdm-k64f-armcc'
mbed-ls: detected NUCLEO_F401RE, console at: COM52, mounted at: F:
        got yotta target 'st-nucleo-f401re-gcc'
mbed-ls: calling yotta to build your sources and tests
info: generate for target: st-nucleo-f401re-gcc 0.0.5 at c:\temp\xxx\mbed-sdk-private\yotta_targets\st-nucleo-f401re-gcc
mbedOS.cmake included
GCC-C.cmake included
mbedOS-GNU-C.cmake included
GCC-GXX.cmake included
mbedOS-GNU-CXX.cmake included
GCC version is: 4.8.4
GNU-ASM.cmake included
-- Configuring done
-- Generating done
-- Build files have been written to: C:/temp/xxx/mbed-sdk-private/build/st-nucleo-f401re-gcc
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
        test 'mbed-test-rtc' ......................................................... FAIL
        test 'mbed-test-echo' ........................................................ OK
        test 'mbed-test-hello' ....................................................... OK
```

# Digesting Test Output

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
$ mbedhtrun -d E: -f ".\build\frdm-k64f-gcc\test\mbed-test-hello.bin" -p COM61 -C 4 -c default -m K64F | mbedgt --digest=stdin -V
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

File ```test.txt``` content:. Run:

```
$ cat test.txt
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

{{ioerr_disk}}
{{end}}
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

# Common Issues

* Issue: In this release there are known issues related to Linux serial port handling during test.
  * Solution: Investigation is ongoing.
* Issue: Some boards show up as 'unknown'.
  * Solution: We will add them in coming releases.
* Issue: Not all mbed platforms have targets mapped to them.
  * Solution: More mbed platforms will be added in coming releases.

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
