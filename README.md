## Descripton
* mbed SDK test framework preview
* This preview is used to show how mbed SDK test suite automates work with mbed enabled board. Test suite consis of few modules used to automate testing:
  * lmtools - module used to detect and list mbed devices connected to your host computer for Widnows and Linux (Ubuntu) platforms.
  * host_tests - module used to supervise automated mbed tests. This module is divided into core host test functionality and plugins scheme in which users can add new plugins whenever they want to exterd functionalities like:
    * mbed platform copy / flash method,
    * mbed platform reset method.
  * meta - temporary module used to store information about host_tests and target platform ids.

### Prerequisites
In order to use test suite with FRDM-K64F board you have to first build FRDM-K64F's mbed SDK and corresponding tests. Tests covering functionality of mbed SDK are located in mbed SDK package and yotta will automatically build tests included in mbed SDK package.
Next step would be to locate on your disk build directory with mbed SDK and configure test suite so it can fetch built tests from build directory. 
Step how to achieve that are described in below 'Usage' chapter of this README file.

### Installation
Note: test suite is Python 2.7.x applciation so you need to install [Python 2.7](https://www.python.org/download/releases/2.7/) to use it in your system.

### Manual installation
You can install this application from sources. Just:
* Clone this repository on your machine:
```
git clone <link_to_this_repository>
```
* Go to directory with repo sources:
```
cd mbed-greentea
```
* Execute pip install command to install package:
```
python setup.py install
```

You should be now able to use mbed.exe command from your command line. 
You can verify if mbed binary (e.g. mbed.exe) is no your system PATH for example by using where command:
```
where mbed.exe
```
```
C:\Python27\Scripts\mbed.exe
```
### Test suite configuration with current yotta K64F build
Please make sure mbed SDK is built with yotta. In build directory you should have target specific subdirectory containing build and tests. For example you've built mbed SDK inside c:\Work directory. Your directory structure should contain:
```
C:\Work\build
└───frdm-k64f-gcc
    ├───CMakeFiles
    ├───source
    ├───test
    ├───ym
    ...
```
where:
* **Work** is directory in which yotta built FRDM-K64F mbed SDK with tests, 
* **frdm-k64f-gcc** contains sources, tests and other build related files.
  * **test** contains binary files with test.

To point test suite to directory containing tests please execute below command. Switch **-l** or **--link-build** is used to point test suite to yotta target's build directory:
```
mbed -l c:\Work\build\frdm-k64f-gcc
```
This will point test suite to location with build's test directory. Test suite will use this location to fetch tests and execute them on target platform.
```
mbed --config
```
above command will prompt:
```
c:\Work\build\frdm-k64f-gcc
```
### List connected mbed enabled devices
Test suite uses lmtools module to detect mbed enabled devices, print current mbeds' configuration.
To list all devices connected to host computer please first connect mbed enabled board using USB cable to your computer and call from command line below test suite command:
```
mbed --list
```
Above command will display currently connected devices. Detection information should contain platform's name (not available for all platforms yet), mbed disk mount point, mbed serial port name and target id. Target id is unique hexadecimal value.
You will later use target id to bind test suite's testing session with particular device.

Example detection listing for Windows 7 OS with three mbed enabled boards connected to host computer:
```
+---------------+-------------+-------------+--------------------------+
| platform_name | mount_point | serial_port | target_id                |
+---------------+-------------+-------------+--------------------------+
| K64F          | E:          | COM61       | 02400203D94B0E7724B7F3CF |
| NRF51822      | F:          | COM58       | 107002161FE6E019E20F0F91 |
| KL22Z         | G:          | COM93       | 0231020337317E7FCACD83B6 |
+---------------+-------------+-------------+--------------------------+
```
Note: FRDM-K64F device is mounted at disk E: and console is available on COM61 serial port. Two other connected to host PC mbed enabled devices boards were detected.

Example detection listing for Ubuntu OS with three mbed enabled boards connected to host computer::
```
+---------------+-------------+--------------+--------------------------+
| platform_name | mount_point | serial_port  | target_id                |
+---------------+-------------+--------------+--------------------------+
| K64F          | /media/usb2 | /dev/ttyACM9 | 02400203D94B0E7724B7F3CF |
| unknown       | /media/usb0 | /dev/ttyACM0 | 066EFF534951775087215736 |
| unknown       | /media/usb1 | /dev/ttyACM1 | 0670FF494956805087154420 |
+---------------+-------------+--------------+--------------------------+
```
Note: FRDM-K64F device is mounted at /media/usb2: and console is available on /dev/ttyACM9 serial port. Two other connected to host PC mbed enabled devices boards were detected (platform name is unknown, reason: current lmtools module limitation).
### Testing session
In order to run test suite and automatically execute available tests we need to specify using commad line switch **-r** which device we want to test (target id is being used bind test suite to device under test). In order to run tests for detected FRDM-K64F platform we need to pass K64F's target id: "02400203D94B0E7724B7F3CF".
```
mbed -r 02400203D94B0E7724B7F3CF
```
or
```
mbed -r 0240
```
to test for each target id starting with '0240' (all FRDM-K64F devices).
Note: You can add switch **--verbose** to see communication between test suite's instrumentation and mbed platform.

Above command will run test suite and execute available tests in build's test directory:
```
testing K64F...
mbed disk: E:
mbed serial: COM61
target test 'mbed-test-basic' executed in 5.99 of 20 sec                        [OK]
target test 'mbed-test-call_before_main' executed in 6.03 of 20 sec             [OK]
target test 'mbed-test-cpp' executed in 6.19 of 20 sec                          [OK]
target test 'mbed-test-cstring' skipped, no automation support yet              [SKIPPED]
target test 'mbed-test-detect' executed in 6.10 of 20 sec                       [OK]
target test 'mbed-test-dev_null' executed in 9.64 of 20 sec                     [OK]
target test 'mbed-test-div' executed in 6.13 of 20 sec                          [OK]
target test 'mbed-test-echo' executed in 12.12 of 20 sec                        [OK]
target test 'mbed-test-hello' executed in 6.00 of 20 sec                        [OK]
target test 'mbed-test-rtc' executed in 10.71 of 20 sec                         [OK]
target test 'mbed-test-stdio' executed in 6.68 of 20 sec                        [OK]
target test 'mbed-test-stl' skipped, no automation support yet                  [SKIPPED]
target test 'mbed-test-ticker' executed in 18.05 of 20 sec                      [OK]
target test 'mbed-test-ticker_2' executed in 17.01 of 20 sec                    [OK]
target test 'mbed-test-ticker_3' executed in 17.09 of 20 sec                    [OK]
target test 'mbed-test-time_us' executed in 16.96 of 20 sec                     [OK]
target test 'mbed-test-timeout' executed in 17.12 of 20 sec                     [OK]
```
Above procedure will flash (copy) each test to mbed's disk, reset device, run test instrumentation and gather test results.

Note: not all tests can be automated at this stage. Those tests will be skipped at this time.

### Command line cheatsheet 
```
mbed --help
Usage: mbed.py [options]

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
  --config              Prompts configuration and exits
  --tests               Prints information about found tests
  --loops=NUMBER        Set no. of loops per test
  -c COPY_METHOD, --copy-method=COPY_METHOD
                        Select binary copy (flash) method. Default is Python's
                        shutil.copy() method. Plugin support: copy, cp,
                        default, eACommander, eACommander-usb, xcopy
  -v, --verbose         Verbose mode (prints some extra information)
```
## Known issues
In this release there are known issues related to Linux serial port handling during test.
Our army of cybernetic organisms is working on fix for this problem as we speak in your mind ;)
