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

## Create simple test case (no mocking)
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
* You've modified only your yotta package.
* You need to only include one header file and specify four macros to complete test case auto- detection by test suite.
  * Test case auto-detection process is a set of prints send by bed device via serial port and read by mbed-host-tests package.
* You specify things like test case timeout, host test, test name etc. in your test case source file.
* In this simple example you do not have to write any Python code to start testing.

## Create test case with simple mocking
In this example we will create more sophisticated test case. In this example we will decide if test passed of failed not in test case during runtime but in host test (mock). We will create host test (a Python script) which will interact with test case running on hardware using serial port connection.


Changes in your yotta module:

1. Create new test case sub-directory and test source code under ```\test``` directory:
2. Populate test case source code with below code:
  ```c++
  #include "mbed/test_env.h"

  #define CUSTOM_TIME  1256729737

  int main() {
      MBED_HOSTTEST_TIMEOUT(20);
      MBED_HOSTTEST_SELECT(rtc_auto);
      MBED_HOSTTEST_DESCRIPTION(RTC);
      MBED_HOSTTEST_START("MBED_16");

      /*
       *
       * This test case is a simple infinite loop printing every 1 second
       * time read from RTC.
       *
       * Note: this test never ends. After flashing and target reset this
       *       test case will print RTC time forever starting from CUSTOM_TIME
       *       timestamp.
       *
       */

      char buffer[32] = {0};
      set_time(CUSTOM_TIME);  // Set RTC time to Wed, 28 Oct 2009 11:35:37
      while(1) {
          time_t seconds = time(NULL);
          strftime(buffer, 32, "%Y-%m-%d %H:%M:%S %p", localtime(&seconds));
          printf("MBED: [%ld] [%s]\r\n", seconds, buffer);
          wait(1);
      }
  }
  ```

Above RTC test case can't be validated during runtime within hardware module.
But we can use our host computer to analyse RTC prints and measure time between  each print (note each RTC status print is every one second).
We need to create new host test script (let's call it ```rtc_auto```; a Python script which can read serial port prints from target:
```
printf("MBED: [%ld] [%s]\r\n", seconds, buffer);
```
and verify if time flows correctly for target's internal RTC.

Changes in mbed-host-tests module:
1. Fork mbed-host-tests module and create new branch which will contain new host test for your RTC test case above.
2. Create new ```rtc_auto.py``` host test script under ```mbed-host-tests/mbed_host_tests/host_tests/``` and populate it with below template:
  ```python
    class TestCaseName_Test():
    
        def test(self, selftest):
            test_result = True
  
            #
            # Here we will implement our host test
            #
  
            return selftest.RESULT_SUCCESS if test_result else selftest.RESULT_FAILURE
  ```

  Note:
  * Each and every host test must be a class with defined ```test(self, selftest)``` method.
    * ```self``` is a standard construct for class methods in Python.
    * ```selftest``` is a ```self``` reference to generic host test class which defines API and enums used for tests.
      * enum ```selftest.RESULT_SUCCESS``` is used to return test case success via host test to test suite.
      * enum ```selftest.RESULT_FAILURE``` is used to return test case success via host test to test suite.
      * enum ```selftest.RESULT_IO_SERIAL``` is used to return serial port error(s) via host test to test suite.
      * ```test(self, selftest)``` method should return at least ```selftest.RESULT_SUCCESS``` on success or ```selftest.RESULT_FAILURE``` for failure.
      * Examples of host test API related to mbed ,-> host test serial port connection communication:
      ```python
      c = selftest.mbed.serial_read(512)
      if c is None:
          return selftest.RESULT_IO_SERIAL
      ```
      
      ```python
      c = selftest.mbed.serial_readline() # {{start}} preamble
      if c is None:
         return selftest.RESULT_IO_SERIAL
      ```
      
      ```python
      # Write bytes to serial port
      selftest.mbed.serial_write(str(random_integer) + "\n")
      ```
      
      ```python
      # Custom initialization for echo test
      selftest.mbed.init_serial_params(serial_baud=self.TEST_SERIAL_BAUDRATE)
      selftest.mbed.init_serial()
      ```
      
      ```python
      # Flush serial port queues (in/out)
      selftest.mbed.flush()
      ```    

3. Implement ```rtc_auto.py``` host test script body:
  ```python
  import re
  from time import time, strftime, gmtime
  
  class RTCTest():
      PATTERN_RTC_VALUE = "\[(\d+)\] \[(\d+-\d+-\d+ \d+:\d+:\d+ [AaPpMm]{2})\]"
      re_detect_rtc_value = re.compile(PATTERN_RTC_VALUE)
  
      def test(self, selftest):
          test_result = True
          start = time()
          sec_prev = 0
          for i in range(0, 5):
              # Timeout changed from default: we need to wait longer for some boards to start-up
              c = selftest.mbed.serial_readline(timeout=10)
              if c is None:
                  return selftest.RESULT_IO_SERIAL
              selftest.notify(c.strip())
              delta = time() - start
              m = self.re_detect_rtc_value.search(c)
              if m and len(m.groups()):
                  sec = int(m.groups()[0])
                  time_str = m.groups()[1]
                  correct_time_str = strftime("%Y-%m-%d %H:%M:%S %p", gmtime(float(sec)))
                  single_result = time_str == correct_time_str and sec > 0 and sec > sec_prev
                  test_result = test_result and single_result
                  result_msg = "OK" if single_result else "FAIL"
                  selftest.notify("HOST: [%s] [%s] received time %+d sec after %.2f sec... %s"% (sec, time_str, sec - sec_prev, delta, result_msg))
                  sec_prev = sec
              else:
                  test_result = False
                  break
              start = time()
          return selftest.RESULT_SUCCESS if test_result else selftest.RESULT_FAILURE
  ```

3. Add ```rtc_auto.py``` to mbed-host-tests registry under ```mbed-host-tests/mbed_host_tests/__init__.py```:
  ```python
  .
  .  
  # Host test supervisors
  .
  .
  from host_tests.rtc_auto import RTCTest
  .
  .
  # Populate registry with supervising objects
  .
  .
  HOSTREGISTRY.register_host_test("rtc_auto", RTCTest())
  .
  .
  ```
  * ```from host_tests.rtc_auto import RTCTest``` is used to import ```rtc_auto.py``` script to this module.
  * ```HOSTREGISTRY.register_host_test("rtc_auto", RTCTest())``` is used to register RTCTest() class implemented in ```rtc_auto.py``` under name ```rtc_auto```.
    
    Note: ```rtc_auto``` is the same name which we are using in test case C/C++ source code via macro: ```MBED_HOSTTEST_SELECT(rtc_auto);```.

4. Use mbed-greenta to determine your platform's yotta target name (e.g. ```frdm-k64f-gcc```) using:
 ```
 $ mbedgt --config
 ```

5. Use mbed-greenta to build test cases and execute them on target:
  ```
  $ mbedgt --target=frdm-k64f-gcc
  ```

## More examples:
* You can refer to existing examples for tests in [mbed-sdk-private](https://github.com/ARMmbed/mbed-sdk-private/tree/master/test) repository.
* All host tests with source code are [here](https://github.com/ARMmbed/mbed-host-tests/tree/master/mbed_host_tests/host_tests).

