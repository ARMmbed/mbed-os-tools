# Description
This document is a simple cookbook introducing testing facilities available for mbed 3.0. From this document you will learn how to:
* Create simple test(s) for your software encapsulated in yotta package.
* Create more complicated test cases where additional mocking / test case supervision is required
* write mocks (we call them **host tests** in mbed) running on test host (your PC / Mac).
This document provides examples for all three methods of testing.

Both test tools and host test scripts are written in Python 2.7. This means minimum knowledge about Python development is required.

## Test process
Currently using test tools you can develop test cases which run on a single hardware platform and can interact with host computer via serial port (series of prints sscanf).

Test tools offer host test functionality. A host test is a supervising Python script executed on host computer (your Mac or PC) and used to mock certain functionality or features like TCP servers required to test your code. Host tests are part of separate Python module (mbed-host-tests).

### Test suite (mbed-greentea)
Test suite called mbed-greentea is Python application which:
* Builds your tests inside your yotta package using ```yotta build``` command.
* For each built test case in your yotta module executes as follows:
  * Flashes hardware (target) with test binary.
  * Resets hardware (target) via serial port (send break command).
  * Listens on target's serial port and scans for prints from target.
  * Executes proper host test which will supervise your test case and
  * extracts test result back to test suite (for reporting).

### Limitations
It is impossible to develop with presented in this documents tools test cases or test scenarios where few mbed devices cooperate with each other. For example it is impossible to write test cases for mesh networks or tests where two mbed devices communicate with each other via sockets / Bluetooth etc.

## yotta package
In order to build tests each test case should be a sub-directory under /test directory located in your yotta package:
```
\your-yotta-pacjage-dir
  \test
    \test_case_1
      source.cpp
      test-case-1.cpp
    \test_case_2
      test-case-2.cpp
    ...
```
All tests in ```\test```'s sub-directories will be build by yotta and test case binaries will be stored in ```\build\<target-name>\test``` directory where ```<target-name>``` is yotta target used to build tests.

It is your responsibility to provide test cases in ```\test``` directory so they will build to target specific binaries.
It is test suite's (mbed-greentea) responsibility to flash all test binaries and perform test supervision by calling host test from mbed-host-tests package.

# Dependencies
* [yotta](https://github.com/ARMmbed/yotta) - yotta is a tool that we're building at mbed.
* [mbed-greentea](https://github.com/ARMmbed/mbed-greentea-private) - test suite for mbed 3.0, codename 'greentea'. The mbed test suite is a collection of tools that enable automated testing on mbed platforms.
* [mbed-ls](https://github.com/ARMmbed/mbed-ls) - mbed-lstools is a module used to detect and list mbed-enabled devices connected via USB port to the host computer.
* [mbed-host-tests](https://github.com/ARMmbed/mbed-host-tests) - Application responsible for target flashing, reset and specific for each test case host test execution.
