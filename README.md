# mbed-host-tests

mbed-host-tests package is decoupled functionality originally implemented for mbedmicro/mbed workspace_tools (See: https://github.com/mbedmicro/mbed). 
Original host tests implementation can be found here: https://github.com/mbedmicro/mbed/tree/master/workspace_tools/host_tests. 
Prerequisites
=====
* Installed Python 2.7.x programming language: https://www.python.org/download/releases/2.7
* Installed pySerial module for Python 2.7: https://pypi.python.org/pypi/pyserial

Rationale
====
With announcement of mbed OS existing mbed SDK and existing test framework will no longer be supported in current state. Monolithic model will be replaced with set of tools and supporting ecosystem which will provide generic and comprehensive services to mbed users, both individual and commercial (partners).

Module responsibilities
====
Mbed ecosystem tools, implemented by mbed users or third party companies can take advantage of existing supplementary module called mbed-host-tests. This module defines classes of host tests that can be reused with new or user defined tests. Host tests also should be shared between mbed classic and mbed OS ecosystems equally.

Module structure
====
```
mbed_host_tests/
    host_tests/             - Supervising host test scripts used for instrumentation. 
    host_tests_plugins/     - Plugins used by host test to flash test runner binary and reset device.
    host_tests_registry/    - Registry, used to store 'host test name' to 'host test class' mapping.
    host_tests_runner/      - Classes implementing basic host test functionality (like test flow control).
```

What is host test?
====
Test suite support test supervisor concept. This concept is realized by separate Python script called "host test" originally stored in mbedmicro/mbed repository under ```mbedmicro/mbed/workspace_tools/host_tests/``` directory. 

Host test script is executed in parallel with test runner (binary running on target hardware) to monitor test execution progress or to control test flow (interact with MUT: mbed device under test). Host test responsibility is also to grab test result or deduce test result depending on test runner behaviour. In many cases  

Basic host test only monitors device's default serial port (serial console or in future console communication channel) for test result prints returned by test runner. Basic test runners supervised by basic host test will print test result in a specific unique format on serial port.

In other cases host tests can for example judge by test runner console output if test passed or failed. It all depends on test itself. In some cases host test can be TCP server echoing packets from test runner and judging packet loss. In other cases it can just check if values returned from accelerometer are actually valid (sane).

```
   <<Target MCU>>                                       <<Host computer>>
+------------------+                               +-------------------------+
|                  |<--- test runner binary copy --|                         |
|  [test runner]...|<--- console communication --->|....[host test runner]   |
|                  |                               |                         |
+------------------+                               +-------------------------+
```

# Installation from Python sources 
Prerequisites: you need to have Python 2.7.x installed on your system.

To install mbed-host-tests module clone mbed-host-tests repository:
```
$ git clone <link-to-mbed-ls-repo>
```
and change directory to mbed-host-tests repository directory:
```
$ cd mbed-host-tests
```
Now you are ready to install mbed-host-tests module. 
```
$ python setup.py install
```
Note: On Linux if you have problem with permissions please try to use ```sudo```:
```
$ sudo python setup.py install
```
To test if your installation succeeded you can use Python interpreter and import ```mbed_host_tests``` to check if module is correctly installed:
```
$ python
Python 2.7.8 (default, Jun 30 2014, 16:03:49) [MSC v.1500 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import mbed_host_tests
>>> dir(mbed_host_tests)
['DefaultAuto', 'DefaultTestSelector', 'DefaultTestSelectorBase', 'DetectPlatformTest', 'DevNullTest', 'EchoTest', 'HOSTREGISTRY', 'HelloTest', 'HostRegistry', 'OptionParser', 'RTCTest', 'StdioTest', 'TCPEchoClientTest', 'TCPEchoServerTest', 'UDPEchoClientTest', 'UDPEchoServerTest', 'WaitusTest', '__builtins__', '__doc__', '__file__', '__name__', '__package__', '__path__', 'get_host_test', 'host_tests', 'host_tests_plugins', 'host_tests_registry', 'host_tests_runner', 'init_host_test_cli_params', 'is_host_test']
```

# Installation from PyPI (Python Package Index)
In the near furure mbed-ls module can be redistributed via PyPI. We recommend you use ```pip``` application. It is available here: https://pip.pypa.io/en/latest/installing.html#install-pip

Note: Python 2.7.9 and later (on the python2 series), and Python 3.4 and later include pip by default, so you may have pip already.
