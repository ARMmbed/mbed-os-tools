* [mbed-host-tests](#mbed-host-tests)
  * [Interaction between the test runner and the host test](#interaction-between-the-test-runner-and-the-host-test)
* [The decoupled module](#the-decoupled-module)
  * [Module responsibilities](#module-responsibilities)
  * [Module structure](#module-structure)
  * [Host test class structure](#host-test-class-structure)
* [Enumeration of host tests](#enumeration-of-host-tests)
* [Example of the CLI version of the host test's DefaultTestSelector supervisor](#example-of-the-cli-version-of-the-host-tests-defaulttestselector-supervisor)
  * [Installation from PyPI (Python Package Index)](#installation-from-pypi-python-package-index)
  * [Installation from Python sources](#installation-from-python-sources)
* [mbedflsh - supporting command line tool for mbed flashing](#mbedflsh---supporting-command-line-tool-for-mbed-flashing)
  * [Example - Default copy method (shell)](#example---default-copy-method-shell)
  * [Example - selecting other available copy method](#example---selecting-other-available-copy-method)
  * [mbedflsh command line switches](#mbedflsh-command-line-switches)

# mbed-host-tests
[![Circle CI](https://circleci.com/gh/ARMmbed/htrun.svg?style=svg)](https://circleci.com/gh/ARMmbed/htrun)

mbed's test suite (codenamed Greentea) supports the *test supervisor* concept. This concept is realised by a separate Python script called "host test", which is executed in parallel with the test runner (a binary running on the target hardware) to monitor the test execution's progress or to control the test flow (interaction with the mbed device under test - MUT). The host test is also responsible for grabbing the test result, or deducing it from the test runner's behaviour.

The basic host test only monitors the device's default serial port (the serial console or - in the future - console communication channel) for test result prints returned by the test runner in a specific and unique format. In other cases, a host test can, for example, judge from the test runner's console output if the test passed or failed. It all depends on the test itself: In some cases the host test can be a TCP server echoing packets from the test runner and judging packet loss. In other cases it can just check whether values returned from an accelerometer are actually valid (sane).

# Writing host tests
When writing a new host test for your module please bear in mind that:
* You own the host test and you should write it the way so it can coexist with the same host tests ran by other processes such as Continuous Integration  systems, other host users etc.
  * Note: If you work in isolation and your test environment if fully controlled by you (for example you queue all tasks calling host tests, or use global host unique socket port numbers) this rule doesn’t apply to you.
* When writing host test using OS resources such as sockets, files, serial ports, peripheral devices like multi-meters /scopes etc. remember that those resources are indivisible!
  * For example if you hardcode in your host test UDP port 32123 and use it for UDP server implementation  of your host test bear in mind that this port may be already used. It is your responsibility to react for this event and implement means to overcome it (if possible).
So you would rather do somethins like this in your host test:
```python
import socket

for port in range(32000, 32100):
    try:
        s.connect((HOSTNAME, PORT))
        ...
        # Got connection on 'port' let's conitnue
        ...
        self.sendToDUTIPandPORT(IP, PORT)
        ...
    except socket.timeout:   
        ...
        continue
else:
    ... 
    # Oh my, none of 3200-32099 ports if available! Let me return an ERROR
    print "No free socket ports available"
    return selftest.RESULT_ERRROR
```
than:
```python
    
PORT = 32123
s.connect((HOSTNAME, PORT))
...
# Got connection on 'port' let's conitnue
...
self.sendToDUTIPandPORT(IP, PORT)
```
  
* Final notes:
  * We do not provide serial port abstraction other that one used for mbed-host test connection. 
  * We do not provide socket abstraction or isolation in host tests and I do not think we will.

## Interaction between the test runner and the host test

```
   <<Target MCU>>                                       <<Host computer>>
+------------------+                               +-------------------------+
|                  |<--- test runner binary copy --|                         |
|  [test runner]...|<--- console communication --->|....[host test runner]   |
|                  |                               |                         |
+------------------+                               +-------------------------+
```

Test runner on the target writes the test case properties like timeout, host test name, description and test_id on the serial port. This helps host test runner to find the required python module in the host tests store for executing the host side of the test.

# The decoupled module

The mbed-host-tests package is a decoupled functionality, originally implemented for [mbedmicro/mbed workspace_tools](https://github.com/mbedmicro/mbed). The original host tests implementation is [available on GitHub](https://github.com/mbedmicro/mbed/tree/master/workspace_tools/host_tests).

With the announcement of mbed OS, the existing mbed SDK and test framework will no longer be supported: the monolithic model will be replaced with a set of tools and supporting an ecosystem that will provide generic and comprehensive services to mbed users, both individual and commercial (partners).

## Module responsibilities

mbed ecosystem tools, implemented by mbed users or third party companies, can take advantage of the existing supplementary module called *mbed-host-tests*. This module defines classes of host tests that can be reused with new or user defined tests. Host tests should also be shared between the mbed classic and mbed OS ecosystems.

## Module structure

```
mbed_host_tests/
    host_tests/             - Supervising host test scripts used for instrumentation.
    host_tests_plugins/     - Plugins used by host test to flash test runner binary and reset device.
    host_tests_registry/    - Registry, used to store 'host test name' to 'host test class' mapping.
    host_tests_runner/      - Classes implementing basic host test functionality (like test flow control).
```

## Host test class structure

```
+-------------------------+
|   DefaultTestSelector   |
+-------------------------+
| run()                   |
+-------------------------+
           _|_
           \_/
+-------------------------+
| DefaultTestSelectorBase |
+-------------------------+
|                         |
+-------------------------+
           _|_
           \_/
+-------------------------+
|          Test           |
+-------------------------+
| Mbed                    |
| host_tests_plugins      |
+-------------------------+
| detect_test_config()    |
| setup()                 |
| run()                   |
+-------------------------+
           _|_
           \_/
+-------------------------+
|     HostTestResults     |
+-------------------------+
| RESULT_SUCCESS          |
| RESULT_FAILURE          |
| RESULT_ERROR            |
| RESULT_IO_SERIAL        |
| RESULT_NO_IMAGE         |
| RESULT_IOERR_COPY       |
| RESULT_PASSIVE          |
| RESULT_NOT_DETECTED     |
+-------------------------+
```

* ```HostTestResults```: defines the generic test result enumeration.
* ```Test```: class encapsulating the ``Mbed``` class and implementing functionalities like host test detection, host test setup and the default ```run()``` function.
* ```Mbed```: implements ways of communicating with an mbed device. It uses the serial port as a standard console communication channel and calls the flash and reset plugins to copy the test runner's binary and reset the mbed device, respectively.
* ```DefaultTestSelectorBase```: base class for the ```DefaultTestSelector``` functionality. Available explicitly in the mbed-host-tests module so users can derive their own ```DefaultTestSelector```s from this base class.
* ```DefaultTestSelector``` : class configured with external options (e.g. input from command line parameters) responsible for test execution flow:
** Copy a given test runner binary to the target MCU (a proper plugin is selected based on your input).
** Reset the target MCU (a proper plugin is selected based on your input).
** Execute the test runner’s test-case-parameters auto-detection process (detects the host test, timeout, test name, test description etc).
** Execute the host test ```test()``` procedure as requested by the test runner.
** Supervise test runner execution (test case flow) with a timeout watchdog.
** Conclude the test case's result. The result can be grabbed from the test runner console output or independently determined by the host test.
** Inform the test suite environment that the test's execution finished.

# Enumeration of host tests

A host test is the implementation derived from the BaseHostTest base class. These classes are looked inside the files in the directory passed with -e or --enum-host-tests= command line argument. One python file may contain multiple host test classes. Found host test classes are stored by their name. If the host test class has an attribute ```name``` then that is used as the host test name. Otherwise python file name is used as the host test name.

In case a host test python file fails to load because of syntax or other error. Following behavior is expected:

* Host test class(es) in the failed file are ignored.
* mbed host test continues to load test classes from other files.
* Test binaries requiring those host test(s) are still flashed and executed. As only binary tells the required host test name.
* The tests will fail with error ```HOST: Error! Unknown host test name 'failed_to_load_module'...```.

Above behavior has an overhead of flashing binaries that will not run. May be in the future a meta data file can be added to help mbed host test to know the test properties before flashing the binary.

# Example of the CLI version of the host test's DefaultTestSelector supervisor

We can use mbed-host-tests in two ways: in our own Python implementation (creating lots of host test variations), or as a predefined and prebuilt default command line tool called ```mbedhtrun``` (**mbed** **h**ost **t**est **run**ner). This default implementation gives us flexibility: we can now use external tools and call the ```mbehtrun``` application without providing extra command line parameters.  This CLI application will do the heavy lifting for modules like ```mbed-greentea```, which will use ```mbehtrun``` to drive each host test session with a given platform.

This is the host test script (```mbedhtrun.py```) used to supervise the test runner execution from the command line:

```python
#!/usr/bin/env python

from mbed_host_tests import DefaultTestSelector         # Default adapter for DefaultTestSelectorBase
from mbed_host_tests import init_host_test_cli_params   # Provided command line options

if __name__ == '__main__':
    # 1. Create DefaultTestSelector object and pass command line parameters
    # 2. Call default test execution function run() to start test instrumentation
    DefaultTestSelector(init_host_test_cli_params()).run()
```

Example of a console call for the above script (```mbedhtrun.py```):

```
$ mbedhtrun.py -d E: -f "C:\Work\mbed\build\test\K64F\ARM\RTOS_7\timer.bin" -p COM61 -C 4 -m K64F
```

Output (real-time console output from the test runner, captured by the host test supervisor over the serial port):

```
MBED: Instrumentation: "COM61" and disk: "E:"
HOST: Copy image onto target...
HOST: Initialize serial port...
HOST: Reset target...
HOST: Property 'timeout' = '15'
HOST: Property 'host_test_name' = 'wait_us_auto'
HOST: Property 'description' = 'Timer'
HOST: Property 'test_id' = 'RTOS_7'
HOST: Start test...
* in 1.00 sec (0.00) [OK]
* in 1.00 sec (0.00) [OK]
* in 1.00 sec (0.00) [OK]
* in 1.00 sec (0.00) [OK]
* in 1.00 sec (0.00) [OK]
* in 1.00 sec (0.00) [OK]
* in 1.00 sec (0.00) [OK]
* in 1.00 sec (0.00) [OK]
* in 1.00 sec (0.00) [OK]
* in 1.00 sec (0.00) [OK]
Consecutive OK timer reads: 10
Completed in 10.00 sec

{{success}}
{{end}}
```
**Note:**

* MUT (mbed under test) is K64F: ```-m K64F```.
* The test runner binary is located at ```C:\Work\mbed\build\test\K64F\ARM\RTOS_7\timer.bin```.
* The K64F virtual serial port (USB CDC) is mounted at ```-p COM61```.
* The K64F virtual serial port (USB MSC) is mounted at ```-d E:```.
* Test result: SUCCESS ```{{success}}}```.
* The test ended after the success code was received: ```{{end}}}```.

##Command line parameters

The default command line parameters deployed with the ```mbed_host_tests``` module are:

```
c:\temp\mbed_host_test_example>mbedhtrun.py --help
Usage: mbedhtrun.py [options]

Options:
  -h, --help            show this help message and exit
  -m MICRO, --micro=MICRO
                        Target microcontroller name
  -p PORT, --port=PORT  Serial port of the target
  -d DISK_PATH, --disk=DISK_PATH
                        Target disk (mount point) path
  -f IMAGE_PATH, --image-path=IMAGE_PATH
                        Path with target's binary image
  -c COPY_METHOD, --copy=COPY_METHOD
                        Copy method selector. Define which copy method (from
                        plugins) should be used
  -C COPY_METHOD, --program_cycle_s=COPY_METHOD
                        Program cycle sleep. Define how many seconds you want
                        wait after copying binary onto target
  -r FORCED_RESET_TYPE, --reset=FORCED_RESET_TYPE
                        Forces different type of reset
  -R NUMBER, --reset-timeout=NUMBER
                        When forcing a reset using option -r you can set up
                        after reset idle delay in seconds
```

#Installation

You can install ```mbed host tests``` using its ```setup.py``` file or using PyPl.

##Prerequisites

Please install:

* [Python 2.7.x](https://www.python.org/download/releases/2.7).
* [The pySerial module for Python 2.7](https://pypi.python.org/pypi/pyserial).

**Note:** if your OS is Windows, please follow the installation instructions [for the serial port driver](https://developer.mbed.org/handbook/Windows-serial-configuration).

## Installation from PyPI (Python Package Index)

mbed-host-tests module is redistributed via PyPI. We recommend you use the [application pip](https://pip.pypa.io/en/latest/installing.html#install-pip).

To install mbed-host-tests from Python Package Index use command:
```
$ pip install mbed-host-tests
```

**Note:** Python 2.7.9 and later (on the Python 2 series), and Python 3.4 and later include pip by default, so you may have pip already.

## Installation from Python sources

Clone the mbed-host-tests GitHub repository:
```
$ git clone <link-to-mbed-ls-repo>
```
Change the directory to the mbed-host-tests's repository directory:
```
$ cd mbed-host-tests
```
Run the setup file:
```
$ python setup.py install
```
**Note:** On Linux, if you have a problem with permissions please try to use ```sudo```:
```
$ sudo python setup.py install
```
To test if your installation succeeded you can use the Python interpreter and import ```mbed_host_tests```:
```
$ python
>>> import mbed_host_tests
>>> dir(mbed_host_tests)
['DefaultAuto', 'DefaultTestSelector', 'DefaultTestSelectorBase', 'DetectPlatformTest',
'DevNullTest', 'EchoTest', 'HOSTREGISTRY', 'HelloTest', 'HostRegistry', 'LWM2MClientAutoTest',
'OptionParser', 'RTCTest', 'RunBinaryOnlyAuto', 'StdioTest', 'TCPEchoClientTest',
'TCPEchoServerTest', 'TCPSocketServerEchoExtTest', 'UDPEchoClientTest', 'UDPEchoServerTest',
'UDPSocketServerEchoExtTest', 'WaitusTest', '__builtins__', '__doc__', '__file__', '__name__',
'__package__', '__path__', 'flash_dev', 'get_host_test', 'get_host_test_list', 'get_plugin_caps',
'host_tests', 'host_tests_plugins', 'host_tests_registry', 'host_tests_runner',
'init_host_test_cli_params', 'is_host_test', 'json', 'reset_dev', 'sleep', 'sys']
```
To start working with ```mbedhtrun``` Python APIs you can experiment with ```flash_dev()``` and ```reset_dev()``` functions.
We can list available mbed devices with ```mbedls``` command:
```
$ mbedls
+--------------+---------------------+------------+------------+---------------------------+
|platform_name |platform_name_unique |mount_point |serial_port |target_id                  |
+--------------+---------------------+------------+------------+---------------------------+
|K64F          |K64F[0]              |F:          |COM4        |0240022648cb1e7700b512e3cf |
+--------------+---------------------+------------+------------+---------------------------+
```
And use Python APIs to flash and reset this device accordingly.
```
$ python
import mbed_host_tests as htrun
>>> htrun.flash_dev(disk='F:',
                    image_path=r'c:\Work\mbed-drivers\build\frdm-k64f-gcc\test\mbed-drivers-test-basic.bin')
        1 file(s) copied.
True
>>> htrun.reset_dev(port='COM4')
True
```
Note: ```c:\Work\mbed-drivers\build\frdm-k64f-gcc\test\mbed-drivers-test-basic.bin``` is valid path to ```K64F``` device's compatible binary.

Example Python API fetch for available plugin capabilities. Note that ```json``` module was used here to pretty print of ```get_plugin_caps``` function.
```
$ python
>>> import mbed_host_tests as htrun
>>> import json
>>> print json.dumps(htrun.get_plugin_caps(), indent=4)
{
    "ResetMethod": [
        "default",
        "eACommander",
        "eACommander-usb",
        "stlink"
    ],
    "CopyMethod": [
        "copy",
        "cp",
        "default",
        "eACommander",
        "eACommander-usb",
        "shell",
        "shutil",
        "stlink",
        "xcopy"
    ]
}
```
You can also check whether ```mbedhtrun``` is correctly installed in your system:
```
mbedhtrun --help
Usage: mbedhtrun-script.py [options]

Options:
  -h, --help            show this help message and exit
  --target=LIST_OF_TARGETS
                        You can specify list of targets you want to build. Use
                        comma to sepatate them
  -n TEST_BY_NAMES, --test-by-names=TEST_BY_NAMES
                        Runs only test enumerated it this switch. Use comma to
                        separate test case names.
  -O, --only-build      Only build repository and tests, skips actual test
                        procedures (flashing etc.)
  -c COPY_METHOD, --copy=COPY_METHOD
                        Copy (flash the target) method selector. Plugin
                        support: copy, cp, default, eACommander, eACommander-
                        usb, shell, xcopy
  --config              Displays connected boards and detected targets and
                        exits.
  --release             If possible force build in release mode (yotta -r).
  --debug               If possible force build in debug mode (yotta -d).
  --digest=DIGEST_SOURCE
                        Redirect input from where test suite should take
                        console input. You can use stdin or file name to get
                        test case console output
  -V, --verbose-test-result
                        Prints test serial output
  -v, --verbose         Verbose mode (prints some extra information)

Example: mbedgt --auto --target frdm-k64f-gcc
```

# mbedflsh - supporting command line tool for mbed flashing
Simple command line tool ```mbedflsh``` is added to help flashing devices from command line. The same functionality can be achieved using ```mbedhtrun``` command line but multiple additional switches may blur way we do it.
This tools will be installed together with ```mbedhtrun``` command line tool.

## Example - Default copy method (shell)
When called without additional switch ```-c``` ```mbedflsh``` will call shell copy command:
* For Windows ```copy``` command and
* for Linux/Mac flavours we will use ```cp``` command.

In this example we will copy file

```
$ mbedflsh -f mbed-drivers-test-echo.bin -d F:
mbedflsh: opening file mbed-drivers-test-echo.bin (...
        1 file(s) copied.
```

## Example - selecting other available copy method

We can force a supported copy method by using ```-c <method>``` switch.

```
$ mbedflsh -f mbed-drivers-test-echo.bin -d F: -c cp
mbedflsh: opening file mbed-drivers-test-echo.bin...
```

See ```mbedflsh -h``` for more details:
```
-c COPY_METHOD, --copy=COPY_METHOD
                    Copy (flash the target) method selector. Plugin
                    support: copy, cp, default, eACommander, eACommander-
                    usb, shell, shutil, stlink, xcopy
```

## mbedflsh command line switches

```
$ mbedflsh -h
Usage: mbedflsh-script.py [options]

Flash mbed devices from command line.This module is using build in to mbed-
host-tests plugins used for flashing mbed devices

Options:
  -h, --help            show this help message and exit
  -f FILENAME, --file=FILENAME
                        File to flash onto mbed device
  -d DISK_PATH, --disk=DISK_PATH
                        Target disk (mount point) path. Example: F:, /mnt/MBED
  -c COPY_METHOD, --copy=COPY_METHOD
                        Copy (flash the target) method selector. Plugin
                        support: copy, cp, default, eACommander, eACommander-
                        usb, shell, shutil, stlink, xcopy
  --plugins             Prints registered plugins and exits
  --version             Prints package version and exits

Example: mbedflsh -d E: -f /path/to/file.bin
```
