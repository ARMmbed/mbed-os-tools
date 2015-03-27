# mbed-host-tests

The mbed-host-tests package is a decoupled functionality originally implemented for the mbedmicro/mbed workspace_tools (See: https://github.com/mbedmicro/mbed). 

The original host tests implementation can be found here: https://github.com/mbedmicro/mbed/tree/master/workspace_tools/host_tests. 

Prerequisites
=====
* Install the Python 2.7.x programming language: https://www.python.org/download/releases/2.7
* Install the pySerial module for Python 2.7: https://pypi.python.org/pypi/pyserial

Rationale
====
With the announcement of mbed OS, the existing mbed SDK and test framework will no longer be supported in their current state. The monolithic model will be replaced with a set of tools and supporting ecosystem which will provide generic and comprehensive services to mbed users, both individual and commercial (partners).

Module responsibilities
====
The mbed ecosystem tools, implemented by mbed users or third party companies, can take advantage of an existing supplementary module called mbed-host-tests. This module defines classes of host tests that can be reused with new or user defined tests. The host tests also should be shared between mbed classic and mbed OS ecosystems equally.

Module structure
====
```

mbed_host_tests/
    host_tests/             - Supervising host test scripts used for instrumentation. 
    host_tests_plugins/     - Plugins used by the host test to flash the test runner binary and reset the device.
    host_tests_registry/    - Registry, used to store the 'host test name' to 'host test class' mapping.
    host_tests_runner/      - Classes implementing the basic host test functionality (like test flow control).

```

What is host test?
====
Test suite supports the test supervisor concept. This concept is realized by a separate Python script called "host test", originally stored in the mbedmicro/mbed repository under the ```mbedmicro/mbed/workspace_tools/host_tests/``` directory. 

The host test script is executed in parallel with the test runner (a binary running on the target hardware) to monitor test execution progress or to control test flow (interacts with the MUT: the mbed device under test). The host test's responsibility is also to grab the test result or deduce the test result depending on the test runner's behaviour. In many cases  

The basic host test only monitors the device's default serial port (the serial console or, in the future, a console communication channel) for test result prints returned by the test runner. Basic test runners supervised by a basic host test will print the test result in a specific unique format on the serial port.

In other cases host tests can for example judge by the test runner's console output whether the test passed or failed. It all depends on the test itself. In some cases the host test can be a TCP server echoing packets from the test runner and judging packet loss. In other cases it can just check if values returned from an accelerometer are actually valid (sane).

## Interaction between the test runner and host test
```
   <<Target MCU>>                                       <<Host computer>>
+------------------+                               +-------------------------+
|                  |<--- test runner binary copy --|                         |
|  [test runner]...|<--- console communication --->|....[host test runner]   |
|                  |                               |                         |
+------------------+                               +-------------------------+
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

* ```HostTestResults``` - Defines the generic test result enum.
* ```Test``` - Class encapsulated ``Mbed class``` and implements functionalities like: host test detection, host test setup and default run() function.
* ```Mbed``` - Implements ways of communicating with an mbed device. Uses serial port as the standard console communication channel and calls the flash and reset plugins to copy the test runner binary and reset the mbed device respectively.
* ``` DefaultTestSelectorBase``` - Base class for the ```DefaultTestSelector``` functionality. Available explicitly in the mbed-host-tests module so users can derive from this base class their own ``` DefaultTestSelector```s.
* ``` DefaultTestSelector``` - Class configured with external options (e.g. input from command line parameters) responsible for test execution flow:
	* Copy a given test runner binary to a target MCU (the proper plugin is selected based on the input options).
	* Reset the target MCU (the proper plugin is selected based on the input options).
	* Execute the test runner’s test case parameters auto-detection process (host test, timeout, test name, test description etc. are detected).
	* Execute requested by the test runner's host test ```test()``` procedure.
	* Supervise the test runner execution (test case flow) with a timeout watchdog.
	* Conclude the test case's result. The result can be grabbed from the test runner console output or determined by the host test independently.
	* Send information about the test execution's end to the test suite environment.

## Example of the CLI version of the host test DefaultTestSelector supervisor
We can use mbed-host-tests in two ways. We can use it in our own Python implementation and create lots of host test variations, or we can use a predefined and built for us command line tool called ```mbedhtrun``` (**mbed** **h**ost **t**est **run**ner).

## Default command line tool
After installing the mbed-host-tests module you will have access to the ```mbehtrun``` (mbed host test runner) CLI application. Below is an example implementation of a user host test runner. This default implementation gives us flexibility. We can now use external tools and call the ```mbehtrun``` application without providing our own. 
This CLI application will do heavy lifting for modules like ```mbed-greentea``` which will use ```mbehtrun``` to drive each host test session with given platform.

Example:

```

$ mbedhtrun -d F: -f ".\build\st-nucleo-f401re-gcc\test\mbed-test-cpp.bin" -p COM52 -C 4 -m NUCLEO_F401RE -c copy
MBED: Instrumentation: "COM52" and disk: "F:"
HOST: Copy image onto target...
        1 file(s) copied.
HOST: Initialize serial port...
HOST: Reset target...
HOST: Unknown property:  Static::init
HOST: Property 'timeout' = '10'
HOST: Property 'host_test_name' = 'default_auto'
HOST: Property 'description' = 'C++'
HOST: Property 'test_id' = 'MBED_12'
HOST: Start test...
Static::stack_test
Stack::init
Stack::hello
Stack::destroy
Static::check_init: OK
Heap::init
Heap::hello
Heap::check_init: OK
Heap::destroy
{{success}}
{{end}}

{{ioerr_serial}}
{{end}}
```

## User implementation
An example of a host test script (```mbedhtrun.py```) used to supervise test runner execution from the command line:
```python
#!/usr/bin/env python

from mbed_host_tests import DefaultTestSelector         # Default adapter for DefaultTestSelectorBase
from mbed_host_tests import init_host_test_cli_params   # Provided command line options

if __name__ == '__main__':
    # 1. Create DefaultTestSelector object and pass command line parameters
    # 2. Call default test execution function run() to start test instrumentation
    DefaultTestSelector(init_host_test_cli_params()).run()
```

Example of a console call for the above example script (```mbedhtrun.py```):
```
$ mbedhtrun.py -d E: -f "C:\Work\mbed\build\test\K64F\ARM\RTOS_7\timer.bin" -p COM61 -C 4 -m K64F
```
Output (real-time console output from a test runner captured by the host test supervisor over serial port):
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
Note: 

* The MUT (mbed under test) is K64F: ```-m K64F```.
* The test runner binary is located at: ```C:\Work\mbed\build\test\K64F\ARM\RTOS_7\timer.bin```. 
* The K64F virtual serial port (USB CDC) is mounted at: ```-p COM61```.
* The K64F virtual serial port (USB MSC) is mounted at: ```-d E:```.
* Test result: SUCCESS - ```{{success}}}```.
* The test ended after the success code was received: ```{{end}}}```.
* The Default command line parameters deployed with ```mbed_host_tests``` module:
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

# Installation from Python sources 
Prerequisites: you need to have Python 2.7.x installed on your system.

To install the mbed-host-tests module clone the mbed-host-tests repository:
```
$ git clone <link-to-mbed-ls-repo>
```
and change the directory to the mbed-host-tests repository directory:
```
$ cd mbed-host-tests
```
Now you are ready to install the mbed-host-tests module. 
```
$ python setup.py install
```
Note: On Linux if you have a problem with permissions please try to use ```sudo```:
```
$ sudo python setup.py install
```
To test if your installation succeeded you can use the Python interpreter and import ```mbed_host_tests``` to check if the module is correctly installed:
```
$ python
Python 2.7.8 (default, Jun 30 2014, 16:03:49) [MSC v.1500 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import mbed_host_tests
>>> dir(mbed_host_tests)
['DefaultAuto', 'DefaultTestSelector', 'DefaultTestSelectorBase', 'DetectPlatformTest', 'DevNullTest', 
'EchoTest', 'HOSTREGISTRY', 'HelloTest', 'HostRegistry', 'OptionParser', 'RTCTest', 'StdioTest', 
'TCPEchoClientTest', 'TCPEchoServerTest', 'UDPEchoClientTest', 'UDPEchoServerTest', 'WaitusTest', 
'__builtins__', '__doc__', '__file__', '__name__', '__package__', '__path__', 'get_host_test', 
'host_tests', 'host_tests_plugins', 'host_tests_registry', 'host_tests_runner', 'init_host_test_cli_params', 
'is_host_test']
```

You can also check if ```mbedhtrun``` is correctly installed on your system:
```
mbedhtrun --help
Usage: mbedhtrun-script.py [options]

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

# Installation from PyPI (Python Package Index)
In the near future the mbed-ls module can be redistributed via PyPI. We recommend you use the ```pip``` application. It is available here: https://pip.pypa.io/en/latest/installing.html#install-pip

Note: Python 2.7.9 and later (on the python2 series), and Python 3.4 and later include pip by default, so you may have pip already.
