# Introduction
Hello and welcome to the mbed SDK test suite, codename 'greentea'. 
The mbed test suite is a collection of tools that enable automated testing on mbed platforms.
The mbed test suite consists of the following modules:

- **[/lmtools](./lmtools)** : module to detect and list connected mbed devices. (Windows/Linux)
- **[/host_tests](./host_tests)** : module with supervised automated tests. There is a *host_tests/plugin* section where users can add plugins to extend the functionality of tests.
- **[/meta](./meta)** : a temporary module used to store information about tests and target platform IDs.

### Supported Platforms
* [FRDM-K64F](http://developer.mbed.org/platforms/FRDM-K64F/) - only platform supported for alpha relese

# Getting Started
To use the mbed test suite you must 
* [install the dependencies](#dependencies)
* [download and install the mbed test suite](#installation)
* [configure the test suite](#test-suite-configuration)

## Dependencies
* [Python2.7](https://www.python.org/download/releases/2.7/) - all host side scripts are written in python
* [yotta](https://github.com/ARMmbed/yotta) - used to build tests from the mbed SDK
* Test binaries built by yotta.

The mbed test suite depends on tests built by **yotta**. Specifically the test suite depends on the tests built as part of the [yotta mbed-sdk repo](https://github.com/armmbed/mbed-sdk).
Instructions on building the yotta mbed-sdk repo can be found in the README.md file for the repo.  
For example, to use the test suite on the FRDM-K64F platform we would first build the [mbed SDK using yotta](https://github.com/ARMmbed/mbed-sdk) with the target set as the FRDM-K64F. 
See the [Yotta Documentation on Building Existing Modules](http://docs.yottabuild.org/tutorial/building.html) for more details. 

## Installation
To install the mbed test suite download the repo and run the setup.py script with the install option.

```Shell
$ git clone https://github.com/ARMmbed/mbed-greentea.git
$ cd mbed-greentea
$ python setup.py install
```

To check that the installer was successful try running the 'mbed --help' command. You should get feedback like below. You may need to restart your terminal first.
```
$ mbed --help
Usage: mbed [options]

This script allows you to run mbed defined test cases for particular MCU(s)
and corresponding toolchain(s).
.
.
.
```

### Uninstall
You can unstall test suite package using pip:

List installed packages and filter for test suite package name:
```
$ pip freeze | grep mbed-testsuite
mbed-testsuite==0.0.2
```

Uninstall test suite package:
```
$ pip uninstall mbed-testsuite
Uninstalling mbed-testsuite:
  c:\python27\lib\site-packages\mbed_testsuite-0.0.2-py2.7.egg
  c:\python27\scripts\mbed-script.py
  c:\python27\scripts\mbed.exe
  c:\python27\scripts\mbed.exe.manifest
Proceed (y/n)? Y
  Successfully uninstalled mbed-testsuite
```

## Test suite configuration
Again, please make sure the [mbed SDK is built with yotta](https://github.com/armmbed/mbed-sdk).

### Find the test build files
Yotta will place the target specific test files in the *yotta_project/build/target_name/test* folder.
For example, if you've built mbed SDK inside *c:/yotta_mbed-sdk/* then the directory should look like this:
```
C:\yotta_mbed-sdk\
└─build
  └─frdm-k64f-gcc
    ├───CMakeFiles
    ├───source
    ├───test          <- This is the folder we want to link to
    ├───ym
    ...
```
where:
* **/build** is directory in which yotta built FRDM-K64F mbed SDK with tests, 
* **frdm-k64f-gcc** contains sources, tests and other build related files.
  * **test** contains binary files with tests.

### Link test files to test suite

You will use **--link-build** or **-l** command line switch to link to platform build directory so test suite can find the tests:
```
--link-build C:\path_to_yotta_mbed-sdk\build\frdm-k64f-gcc
```

To verify if your link is set correctly you can point test suite to yotta build with SDK and 
```
$ mbed --tests --link-build C:\path_to_yotta_mbed-sdk\build\frdm-k64f-gcc
```
This should print information about the tests provided by the built directory. If it prints nothing you have no tests:
```
mbed-test-blinky.bin
mbed-test-ticker_3.bin
mbed-test-detect.bin
mbed-test-rtc.bin
mbed-test-time_us.bin
mbed-test-stl.bin
mbed-test-ticker_2.bin
mbed-test-stdio.bin
mbed-test-cstring.bin
mbed-test-call_before_main.bin
mbed-test-dev_null.bin
mbed-test-sleep_timeout.bin
mbed-test-serial_interrupt.bin
mbed-test-timeout.bin
mbed-test-basic.bin
mbed-test-cpp.bin
mbed-test-div.bin
mbed-test-echo.bin
mbed-test-ticker.bin
mbed-test-hello.bin
mbed-test-heap_and_stack.bin
```


# Usage
  * [list connected devices](#list-connected-mbed-devices)
  * [run automated tests](#run-automated-tests)

## List connected mbed devices
List connected mbed devices and configuration information: <br>
**Note:** On Windows you must have the [mbed driver](http://developer.mbed.org/handbook/Windows-serial-configuration) installed for this to work. Linux / OSX work just fine natively. 
```
$ mbed --list
```
This command will print out the platform's name (not available for all platforms yet), mount point, serial port name and target ID. The Target ID is unique hexadecimal value.
The Target ID is used for running automated tests on a board, more on this in the [testing section](#running-automated-tests).

#### Examples
**Example 1:** Windows 7 OS with three mbed boards connected to host computer:
```
$ mbed --list
+---------------+-------------+-------------+--------------------------+
| platform_name | mount_point | serial_port | target_id                |
+---------------+-------------+-------------+--------------------------+
| K64F          | E:          | COM61       | 02400203D94B0E7724B7F3CF |
| NRF51822      | F:          | COM58       | 107002161FE6E019E20F0F91 |
| KL22Z         | G:          | COM93       | 0231020337317E7FCACD83B6 |
+---------------+-------------+-------------+--------------------------+
```
**Note:** FRDM-K64F device is mounted at disk E: and console is available on COM61 serial port. Two other connected to host PC mbed enabled devices boards were detected.

**Example 2:** Ubuntu OS with three mbed boards connected to host computer::
```
$ mbed --list
+---------------+-------------+--------------+--------------------------+
| platform_name | mount_point | serial_port  | target_id                |
+---------------+-------------+--------------+--------------------------+
| K64F          | /media/usb2 | /dev/ttyACM9 | 02400203D94B0E7724B7F3CF |
| unknown       | /media/usb0 | /dev/ttyACM0 | 066EFF534951775087215736 |
| unknown       | /media/usb1 | /dev/ttyACM1 | 0670FF494956805087154420 |
+---------------+-------------+--------------+--------------------------+
```
**Note:** FRDM-K64F device is mounted at /media/usb2: and console is available on /dev/ttyACM9 serial port. Two other connected to host PC mbed enabled devices boards were detected (platform name is unknown, reason: current lmtools module limitation).

## Running Automated Tests
Use the **--run** or **'-r'** switch to run automated tests. Select which device to run tests on by specifying the Target ID of the device. 
```
$ mbed -r target_id --link-build C:\path_to_yotta_mbed-sdk\build\frdm-k64f-gcc
```
#### Examples
The tests will flash (copy) each test to mbed's disk, reset device, run test instrumentation and gather test results.<br>
**Note:** not all tests can be automated at this stage. Those tests will be skipped at this time.

**Example 1:** Run test suite on the K64F<br>
The target ID is taken from the 'mbed --list' output from previous section
```
$ mbed -r 02400203D94B0E7724B7F3CF --link-build C:\path_to_yotta_mbed-sdk\build\frdm-k64f-gcc
```

**Example 2:** multiple boards at once<br>
The Target ID can be shortened to the minimum unique string length. This command will test every device with a target ID that starts with '0240' (all FRDM-K64F devices).
```
$ mbed -r 0240 --link-build C:\path_to_yotta_mbed-sdk\build\frdm-k64f-gcc
```

**Example 3:** Verbose mode for more details.<br>
You can add switch **--verbose** or **-v** switch to see communication between test suite's instrumentation and mbed platform.
This command will run test suite and execute available tests in build's test directory:
```
$ mbed -r 0240 --link-build C:\path_to_yotta_mbed-sdk\build\frdm-k64f-gcc
testing K64F...[E:, COM61]
target test 'mbed-test-basic' executed in 7.80 of 20 sec                        [OK]
target test 'mbed-test-blinky' skipped, no automation support yet               [SKIPPED]
target test 'mbed-test-call_before_main' executed in 7.82 of 20 sec             [OK]
target test 'mbed-test-cpp' executed in 8.79 of 20 sec                          [OK]
target test 'mbed-test-cstring' skipped, no automation support yet              [SKIPPED]
target test 'mbed-test-detect' executed in 7.83 of 20 sec                       [FAIL]
target test 'mbed-test-dev_null' executed in 13.76 of 20 sec                    [OK]
target test 'mbed-test-div' executed in 7.92 of 20 sec                          [OK]
target test 'mbed-test-echo' executed in 16.08 of 20 sec                        [OK]
target test 'mbed-test-heap_and_stack' skipped, no automation support yet       [SKIPPED]
target test 'mbed-test-hello' executed in 7.75 of 20 sec                        [OK]
target test 'mbed-test-rtc' executed in 12.79 of 20 sec                         [OK]
target test 'mbed-test-serial_interrupt' skipped, no automation support yet     [SKIPPED]
target test 'mbed-test-sleep_timeout' skipped, no automation support yet        [SKIPPED]
target test 'mbed-test-stdio' executed in 9.75 of 20 sec                        [OK]
target test 'mbed-test-stl' skipped, no automation support yet                  [SKIPPED]
target test 'mbed-test-ticker' executed in 20.61 of 20 sec                      [OK]
target test 'mbed-test-ticker_2' executed in 19.59 of 20 sec                    [OK]
target test 'mbed-test-ticker_3' executed in 19.61 of 20 sec                    [OK]
target test 'mbed-test-time_us' executed in 18.68 of 20 sec                     [OK]
target test 'mbed-test-timeout' executed in 19.64 of 20 sec                     [OK]
```

## Command line cheatsheet 
This is the output of 'mbed --help' and is provided for reference
```
Usage: mbed-script.py [options]

This script allows you to run mbed defined test cases for particular MCU(s)
and corresponding toolchain(s).

Options:
  -h, --help            show this help message and exit
  -l LINK_BUILD, --link-build=LINK_BUILD
                        Point to build directory with target specific yotta
                        build
  --list                Prints information about detected mbed enabled
                        platforms
  -r TARGET_ID, --run=TARGET_ID
                        Executes test suite automation on given mbed platfrom
                        (by target id)
  --tests               Prints information about found tests
  --loops=NUMBER        Set no. of loops per test
  -v, --verbose         Verbose mode (prints some extra information)
```
## Common Issues
* Issue: In this release there are known issues related to Linux serial port handling during test.
  * Solution: Our army of cybernetic organisms is working on fix for this problem as we speak in your mind ;)
* Issue: Some boards show up as 'unknown'
  * Solution: we will add them in coming releases
* Issue: 'mbed --tests' doesn't print anything
  * Solution: You either are not linking to the correct directory, or yotta didnt build any tests. 
