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

Test tools are designed in such a way that you can concentrate on test development and (re)use existing host tests.

### Test suite (mbed-greentea)
Mbed 3.0 test suite called mbed-greentea is a Python 2.7 application which:
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
Place your test case under a sub-directory of ```\test``` directory located in your yotta package:
```
\your-yotta-pacjage-dir
  \source
    ...
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

## yotta's testDependencies
The [testDependencies](http://docs.yottabuild.org/reference/module.html#testDependencies) section can be used to list modules that are only depended on by tests. They will not normally be installed if your module is installed as a dependency of another.

In our case we need to add testDependencies to ```mbed-sdk-private``` so we can include test related macros from ```mbed/test_env.h``` header file. Test macros will be explained in following sections of this document.

# Dependencies
* [yotta](https://github.com/ARMmbed/yotta) - yotta is a tool that we're building at mbed.
* [mbed-greentea](https://github.com/ARMmbed/mbed-greentea-private) - test suite for mbed 3.0, codename 'greentea'. The mbed test suite is a collection of tools that enable automated testing on mbed platforms.
* [mbed-ls](https://github.com/ARMmbed/mbed-ls) - mbed-lstools is a module used to detect and list mbed-enabled devices connected via USB port to the host computer.
* [mbed-host-tests](https://github.com/ARMmbed/mbed-host-tests) - Application responsible for target flashing, reset and specific for each test case host test execution.

# Examples
In this section we will show how to create few flavours of test cases for your yotta package with mbed-greentea and mbed-host-tests.

## Create simple test
Often your test case will be a ```main()``` function with collection of API function calls. No special mocking is required and you can determine test case result in runtime. In that case you can use build-in host test and just implement your test case's main() function.

To do so just:

1. Create new test case sub-directory and test source code under ```\test``` directory:
2. Populate test case source code with below template:
  ```c++
  #include "mbed/test_env.h"
  
  int main() {
      MBED_HOSTTEST_TIMEOUT(20);
      MBED_HOSTTEST_SELECT(default);
      MBED_HOSTTEST_DESCRIPTION(Basic);
      MBED_HOSTTEST_START("MBED_A1");
      
      int result = 0; // 0 - false, !0 - true
      
      /*
       * Call your API function(s) here and
       * calculate 'result' in runtime.
       * Set 'result' with  true / false success code
       */
      
      MBED_HOSTTEST_RESULT(result);
  }
  ```
3. Use ```yotta build``` command to check if your test case compiles and builds before adding it to yotta module.
4. Connect mbed device to your computer (host) using USB.
5. Use mbed-greenta to determine your platform's yotta target name (e.g. ```frdm-k64f-gcc```) using:
 ```
 $ mbedgt --config
 ```

6. Use mbed-greenta to build test cases and execute them on target:
  ```
  $ mbedgt --target=frdm-k64f-gcc
  ```

Note:
* Use below command to only build your package from soruces with tests:
  ```
  $ mbedgt --target=frdm-k64f-gcc -O
  ```

* Use option ```-V``` to display serial port communication between host computer and mbed device on your console.
* Use option ```-n <test-name>``` to execute only test case by given name. You can use comma to execute more than one test case. ```<test-name>``` is test case binary name without extension.

### Notes:
* We've included ```mbed/test_env.h``` to get access to generic mbed test ```MBED_HOSTTEST_*``` macros. These macros are used to pass to test suite information about above test case properties like: 
  * ```MBED_HOSTTEST_TIMEOUT```: Test case timeout, in this case 20 sec.
  * ```MBED_HOSTTEST_SELECT```: Host test name (which host test should be used to supervise this test), in this case 'default' host test available in standard mbed-host-tests package distribution.
  * ```MBED_HOSTTEST_DESCRIPTION```: Simple test case description; currently ignored by test suite.
  * ```MBED_HOSTTEST_START```: Marks test case execution start. Additionally carries simple test case name; currently ignored by test suite. After this macro is executed host test specified in ```MBED_HOSTTEST_SELECT``` will be executed.
  * ```MBED_HOSTTEST_RESULT``` macro is used to pass to test suite test case result: true (pass) / false (failed).

Above model have few advantages:
* You need to only include one header file and specify four macros to complete test case auto- detection by test suite.
  * Test case auto-detection process is a set of prints send by bed device via serial port and read by mbed-host-tests package.
* You specify things like test case timeout, host test, test name etc. in your test case source file.
* In this simple example you do not have to write any Python code to start testing.
