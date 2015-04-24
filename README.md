# Introduction
Hello and welcome to the mbed SDK test suite, codename 'greentea'.
The mbed test suite is a collection of tools that enable automated testing on mbed platforms.
The mbed test suite imports and uses following modules:

* mbed-ls (tools/mbed-ls)
* mbed-host-tests (tools/mbed-host-tests)

Make sure you've installed Python and the Python modules listed above. You can check it by typing:
```
$ python --version
```
```
$ pip freeze | grep mbed
mbed-greentea==0.0.5
mbed-host-tests==0.1.4
mbed-ls==0.1.5
```

Note: **At this current time, the test framework is targeted to run on Windows OS.**

## Supported mbed platforms
* [FRDM-K64F](http://developer.mbed.org/platforms/FRDM-K64F/).
* [NUCLEO_F401RE](http://developer.mbed.org/platforms/ST-Nucleo-F401RE/).

## Supported yotta targets
* ```frdm-k64f-gcc```.
* ```frdm-k64f-armcc```.
* ```st-nucleo-f401re-gcc```.

Note: More platforms and yotta targets will be added. In most cases only meta-data must be updated for each platform and target.

# Getting Started
To use the mbed test suite you must:
* Install the dependencies.
* Download and install the mbed test suite.
* Download mbed SDk sources.

## Dependencies
* [Python2.7](https://www.python.org/download/releases/2.7/) - all host side scripts are written in python.
    * Note: If you do not have python installed already, [Python2.7.9](https://www.python.org/downloads/release/python-279/) is recommended.
* [pip](https://pypi.python.org/pypi/pip) is required, however it is bundled with Python 2.7.9
    * To check if pip is installed, run ```$ pip --version```
* Python [setuptools](https://pythonhosted.org/an_example_pypi_project/setuptools.html) to install dependencies.
* [yotta](https://github.com/ARMmbed/yotta) - used to build tests from the mbed SDK.
* mbed-ls (tools/mbed-ls)
* mbed-host-tests (tools/mbed-host-tests)
* Some Nucleo boards like F401RE can be correctly flashed only with ```cp``` or ```copy``` command line command. make sure in your system there is a ```cp``` shell command installed. It can be available by default (LInux OS) or provided by environments such as ```git```. We will assume you've installed ```git``` command line tools for Windows and ```cp``` command is available.

## Installation
To install the mbed test suite download the repo and run the setup.py script with the install option.
```
$ cd tools/mbed-greentea
$ python setup.py install
```

Use the same procedure to install dependencies ```mbed-ls``` and ```mbed-host-tests```.

To check that the installer was successful try running the ```mbedgt --help``` command. You should get feedback like below. You may need to restart your terminal first.
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

## Uninstall
You can unstall test suite package using ```pip```. List installed packages and filter for test suite package name:
```
$ pip freeze | grep mbed-greentea
mbed-greentea==0.0.5
```

Uninstall test suite package:
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

# Environment precheck
At this point you should install all dependencies and be ready to build mbed SDK and perform automated testing.
In current configuration mbed test suite can automatically detect most of popular mbed-enabled platforms connected to host via USB interface.

Test suite is using ```mbed-ls``` module to check connected devices and. Separate module called ```mbed-host –tests``` is used to flash and supervise each platforms test. This decoupling allows us to make better software and maintain each or the functionalities as separate domain. Previously mbed SDK test suite consisted of mentioned modules which is not good for maintainability and stopped us from building more efficient tools.

Make sure you have all tools installed. For example you can list all mbed devices connected to your host computer:
```
$ mbedls
+---------------------+-------------------+-------------------+--------------------------------+
|platform_name        |mount_point        |serial_port        |target_id                       |
+---------------------+-------------------+-------------------+--------------------------------+
|K64F                 |E:                 |COM61              |02400203D94B0E7724B7F3CF        |
|NUCLEO_F401RE        |F:                 |COM52              |07200200073E650A385BF317        |
+---------------------+-------------------+-------------------+--------------------------------+
```

# Digesting test output
The test suite now has a new feature for digesting input, which is activated with the ```--digest``` command line switch. Now you can pipe your proprietary test runner’s console output to the test suite or just ```cat``` a file with the test runner’s console output. You can also just specify file name which will be digested as the test runner's console input.

This option allows you to write your own automation where you execute the test runner or just feed the test suite with the test runner’s console output.  The test suite parses the console output to determine whether it indicates success for failure, then returns that status to the test environment.
Note:
* ```--digest=stdin``` will force ```stdin``` to be the default test suite input.
* ```--digest=filename.txt``` will force ```filename.txt``` file content to be the default test suite input.

The examples below demonstrate the use of the ```--digest``` option. Assume that you have written a test runner in ```bash``` shell scripting, or just collected a bunch of test results in a database and the test console output is available.
To get the mbed test suite's predefined test results, you must scan the console output from the tests. Note: test suite results and tags are encoded between double curly braces.
For example, a typical success code looks like this: ```{{success}}{{end}}```.

## Example 1 - Digest the default mbed host test runner
You can run mbed host tests with ```mbed-host-tests``` ```mbedhtrun``` to evaluate the existing test cases' test results (Test results are returned to the environment as ```mbedgt``` return codes; the success code is ```0```).

```
$ mbedhtrun -d E: -f ".\build\frdm-k64f-gcc\test\mbed-test-hello.bin" -p COM61 -C 4 -c default -m K64F | mbedgt --digest=stdin -V

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
File ```test.txt``` content:
```
$ cat test.txt
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

# Testing
To test a platform, the mbed SDK sources are required.  These are provided in the release sources under the libraries/mbed-sdk directory. The hardware test platform is also required; currently two targets are supported: Freescale FRDM-K64F and ST Nucleo-F401RE.

Change directories to the mbed sources:
```
$ cd libraries/mbed-sdk
```

First, examine the current configuration:
```
$ mbedgt –config
mbed-ls: detecting connected mbed-enabled devices...
mbed-ls: detected K64F, console at: COM61, mounted at: E:
        got yotta target 'frdm-k64f-gcc'
        got yotta target 'frdm-k64f-armcc'
mbed-ls: detected NUCLEO_F401RE, console at: COM52, mounted at: F:
        got yotta target 'st-nucleo-f401re-gcc'
```
Here, ```mbedgt``` detected (using ```mbed-ls``` module) two boards connected to host system: ``` K64F```, ```NUCLEO_F401RE ```.

For each ```mbedgt``` proposed a few supported yotta targets:
* ```frdm-k64f-gcc``` - Freescale K64F platform compiled with GCC cross-compiler.
* ```frdm-k64f-armcc``` - Freescale K64F platform compiled with Keil armcc cross-compiler.
* ```st-nucleo-f401re-gcc```- STMicro Nucleo F401RE platform compiled with GCC cross-compiler.

For simplicity, only the GCC targets are described below.  To build the targets, the test suite can be used to invoke yotta indirectly.

In this example, ```--target``` is used to specify the targets which the test suite will interact with.  Option ```-O``` is used to tell the test suite to only build sources and tests, but not to run the tests.

```
$ mbedgt --target=frdm-k64f-gcc,st-nucleo-f401re-gcc -O
mbed-ls: detecting connected mbed-enabled devices...
mbed-ls: detected K64F, console at: COM61, mounted at: E:
        got yotta target 'frdm-k64f-gcc'
mbed-ls: calling yotta to build your sources and tests
warning: uvisor-lib has invalid module.json:
warning:   author value [u'Milosch Meriac <milosch.meriac@arm.com>', u'Alessandro Angelino <alessandro.angelino@arm.com>'] is not valid under any of the given schemas
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

Now that the tests are built, the test suite can be called again to run the tests.  From the same director, invoke ```mbedgt``` again as shown below:
```
$ mbedgt --target=frdm-k64f-gcc,st-nucleo-f401re-gcc
mbed-ls: detecting connected mbed-enabled devices...
mbed-ls: detected K64F, console at: COM61, mounted at: E:
        got yotta target 'frdm-k64f-gcc'
mbed-ls: calling yotta to build your sources and tests
warning: uvisor-lib has invalid module.json:
warning:   author value [u'Milosch Meriac <milosch.meriac@arm.com>', u'Alessandro Angelino <alessandro.angelino@arm.com>'] is not valid under any of the given schemas
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

# Common Issues
* Issue: In this release there are known issues related to Linux serial port handling during test.
  * Solution: Investigation is ongoing.
* Issue: Some boards show up as 'unknown'
  * Solution: we will add them in coming releases
* Issue: Not all mbed platforms have targets mapped to them.
  * Solution: More mbed platforms will be added in coming releases.
