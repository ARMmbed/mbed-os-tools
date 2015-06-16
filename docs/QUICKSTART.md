# Description

This document is a simple cookbook introducing the testing facilities available for mbed 3.0. From this document you will learn how to:

* Create simple test(s) for your software, encapsulated in a yotta package. To read the full yotta documentation go [here](http://docs.yottabuild.org/reference/commands.html).
* Create more complicated test cases where additional mocking or test case supervision is required.
* Write mocks (we call them **host tests** in mbed) running on the test host (your PC or Mac).

This document provides examples for all three methods of testing.

* You can also create [unit tests](http://en.wikipedia.org/wiki/Unit_testing) with the [mbed compatible CppUTest library](https://github.com/ARMmbed/mbed-cpputest-private). Information about the CppUTest library can be found [here](https://cpputest.github.io/manual.html).

Both test tools and host test scripts are written in Python 2.7. This means some knowledge about Python development is required.

## Test process

By using these test tools you can develop test cases that run on a single hardware platform and can interact with the host computer via the serial port (a series of ```print```s and ```sscanf``` calls). The host computer communicates with the mbed device using a serial port connection (duplex) to drive test scenarios.

Test tools offer a [host test](https://github.com/ARMmbed/mbed-host-tests) functionality. A host test is a supervising Python script executed on the host computer (your Mac or PC) and used to mock a certain functionality or feature like a TCP server required to test your code. Host tests are part of a separate Python module (mbed-host-tests).

Each host test should be as generic as possible, so that many test cases running on mbed platforms can reuse it. For example a simple TCP or UDP echo server can be used to test different network APIs, include those for mbed 2.0.

Test tools are designed to let you:

* Concentrate on test development rather than test framework building.
* (Re)use existing host tests. 
* Create new host tests to cover new functional and interoperability domains.

### Test suite (mbed-greentea)

Mbed 3.0 test suite, called mbed-greentea, is a Python 2.7 application that:

* Builds your tests inside your yotta package using the ```yotta build``` command.
  * List all tests in \build\<target_name>\test.
* For each build's test case in your yotta module, mbed-greentea executes actions in the following order:
  * Flash the hardware (target) with the test binary.
  * Reset the hardware (target) via the serial port (send break command).
  * Listen on the target's serial port and scan for prints from the target.
  * Execute the proper host test to supervise your test case.
  * Pass the test result back to the test suite (for reporting).

### Limitations
1. It is impossible to develop (with the current test tools) test cases or test scenarios where several mbed devices cooperate with each other. For example, it is impossible to write test cases for mesh networks or tests where two mbed devices communicate with each other via sockets, Bluetooth etc.
2. mbed-greentea doesn't support resource locking (mutually exclusive access to hardware platform), so running severe; instances of mbed-greentea for the same target may cause undefined behaviour. In case of multiple test suite instances, please manually control resource access. When using a Continuous Integration system you can configure dependencies for CI jobs, and by that control access to each device under test.
3. You can't mix unit tests written using the CppUTest library with 'hello world' tests. The reason is that the CppUTest library defines its own ```main()``` function, which will be linked with every test. Currently the yotta package can't be configured to link each test separately with different a test library.

## yotta package
Place your test case under a sub-directory of the ```\test``` directory located in your yotta package:

Note: For details please check ['The ```test``` Directory' section of the yotta documentation](http://docs.yottabuild.org/tutorial/testing.html).

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

All tests in ```\test```'s sub-directories will be built by yotta, and the test case binaries will be stored in the ```\build\<target-name>\test``` directory where ```<target-name>``` is the yotta target used to build tests.

It is your responsibility to provide test cases in the ```\test``` directory so they will build to target-specific binaries. It is test suite's (mbed-greentea) responsibility to flash all test binaries and perform test supervision by calling the host test from the mbed-host-tests package.

## yotta's testDependencies
The [testDependencies](http://docs.yottabuild.org/reference/module.html#testDependencies) section can be used to list modules that are only depended on by tests. They will not normally be installed if your module is installed as a dependency of another.

In our case we need to add testDependencies to ```mbed-sdk-private``` so we can include test-related macros from the ```mbed/test_env.h``` header file. Test macros will be explained in the next sections of this document.

# Dependencies
* [yotta](https://github.com/ARMmbed/yotta): a building tool that we'll be using instead of the bundled builder of mbed OS 2.
* [mbed-greentea](https://github.com/ARMmbed/mbed-greentea-private): the test suite for mbed 3.0, codename 'greentea'. The mbed test suite is a collection of tools that enable automated testing on mbed platforms.
* [mbed-ls](https://github.com/ARMmbed/mbed-ls): mbed-lstools is a module used to detect and list mbed-enabled devices connected to the host computer over USB.
* [mbed-host-tests](https://github.com/ARMmbed/mbed-host-tests): the application responsible for target flashing and reset, and specific for each host test execution of a test case.

# Examples
In this section we will show you how to create a few flavours of test cases for your yotta package with mbed-greentea and mbed-host-tests.

## Creating a simple test case (no mocking)
Often your test case will be a ```main()``` function with a collection of API function calls. No special mocking is required and you can determine the test case's result in runtime. In that case you can use a built-in host test and just implement your test case's main() function.

Use:

```c++
#include "mbed/test_env.h"
```
in your code to include the mandatory macros required to drive the test case on hardware.

To do so just:

1. Create a new test case sub-directory and test source code under the ```\test``` directory.
2. Populate the test case source code with the following template:
	
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
3. Use the ```yotta build``` command to check if your test case compiles and builds before adding it to the yotta module.
4. Connect an mbed device to your computer (host) using USB.
5. Use mbed-greenta to determine your platform's yotta target name (e.g. ```frdm-k64f-gcc```) using:
 ```
 $ mbedgt --config
 ```

6. Use mbed-greenta to build test cases and execute them on the target:
  ```
  $ mbedgt --target=frdm-k64f-gcc
  ```

Note:

* Use the following command to only build your package from sources with tests:
  ```
  $ mbedgt --target=frdm-k64f-gcc -O
  ```

* Use the option ```-V``` to display the serial port communication between the host computer and the mbed device on your console.
* Use the option ```-n <test-name>``` to execute only a specific test (using name matching). You can use a comma to execute more than one test case. ```<test-name>``` is the name of the test case's binary (without an extension).

### Notes
* We've included ```mbed/test_env.h``` to get access to the generic mbed test's ```MBED_HOSTTEST_*``` macros. These macros are used to pass to the test suite information about the above test case. For example: 
  * ```MBED_HOSTTEST_TIMEOUT```: Test case timeout, in this case 20 seconds.
  * ```MBED_HOSTTEST_SELECT```: Host test name (which host test should be used to supervise this test). In this case the 'default' host test that's available in the standard mbed-host-tests package distribution.
  * ```MBED_HOSTTEST_DESCRIPTION```: A simple test case description; currently ignored by the test suite.
  * ```MBED_HOSTTEST_START```: Marks the test case's execution start. Additionally, it carries a simple test case name, which is currently ignored by the test suite. After this macro is executed the host test specified in ```MBED_HOSTTEST_SELECT``` will be executed.
  * The ```MBED_HOSTTEST_RESULT``` macro is used to pass to test suite test case result: true (pass) or false (failed).

The above model has a few advantages:

* You've modified only your yotta package.
* You only need to include one header file and specify four macros to complete the test case's auto-detection by the test suite.
  * The test case auto-detection process is a set of prints sent by the mbed device via the serial port and read by the mbed-host-tests package.
* You specify things like test case timeout, host test and test name in your test case's source file.
* In this simple example you do not have to write any Python code to start testing.

## Creating a test case with simple mocking
In this example we will create a more sophisticated test case. We will decide whether the test passed of failed not in the test case during runtime but in the host test (mock). We will create a host test (a Python script) that will interact with the test case running on the hardware using a serial port connection.

Changes in your yotta module:

1. Create a new test case sub-directory and test source-code under the ```\test``` directory.
2. Populate the test case's source code with the following code:
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

The above RTC test case can't be validated during runtime within the hardware module. But we can use our host computer to analyse the RTC prints and measure the time between each print (note that RTC status prints are once every second).

We need to create a new host test script (let's call it ```rtc_auto``` for now). We will use a macro:
```c++
MBED_HOSTTEST_SELECT(rtc_auto);
```
to tell the test suite which host test is used to instrument the above code. Our ```rtc_auto``` script is a Python script that will read and parse the serial port prints from the target: 
```c++
printf("MBED: [%ld] [%s]\r\n", seconds, buffer);
```
It will also verify that time flows correctly for the target's internal RTC, based on the time intervals between those prints.

Changes in the mbed-host-tests module:

1. Fork the mbed-host-tests module and create a new branch that will contain a new host test for your RTC test case above.
2. Create a new ```rtc_auto.py``` host test script under ```mbed-host-tests/mbed_host_tests/host_tests/``` and populate it with the following template:
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
  * Each and every host test must be a class with a defined ```test(self, selftest)``` method.
    * ```self``` is a standard construct for class methods in Python.
    * ```selftest``` is a ```self``` reference to a generic host test class that defines the API and enums used for tests.
      * Enum ```selftest.RESULT_SUCCESS``` is used to return the test case's success via the host test to the test suite.
      * Enum ```selftest.RESULT_FAILURE``` is used to return the test case's failure via the host test to the test suite.
      * Enum ```selftest.RESULT_IO_SERIAL``` is used to return serial port error(s) via the host test to the test suite.
      * The ```test(self, selftest)``` method should return at least ```selftest.RESULT_SUCCESS``` on success or ```selftest.RESULT_FAILURE``` on failure.
      * Examples of the host test API, related to mbed to host test serial port communication:
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
      
      ```python
      # We want to dump the serial port while the test is ongoing
      #
      # This function is non-blocking so you can continue to execute your test case,
      # but remember that serial port data is dumped in the background (in a separate thread)
      # so you can't access serial port data using the selftest.mbed.serial_* functions reliably.
      #
      # This function is useful when you only want to dump serial port data and test case
      # flow is controlled over different media like sockets or, for example, Bluetooth or BLE
      # communication.
      selftest.dump_serial()
      ```    
      
      ```python
      # Stop serial port in background initiated with selftest.dump_serial() method
      selftest.dump_serial_end()
      ```
      
      ```python
      # Read test configuration data passed to host test from command line, option --test-cfg=<JSON_FILE>
      test_cfg = selftest.mbed.test_cfg 
      ```
      Note: You can pass extra test configuration data to host tests. Define JSON formated file and use command line option ```--test-cfg``` to define path for that file. JSON test configuration file will be loaded (if possible) from file and stored in above data structure. This is very flexible feature but limits users to define only one JSON configuration file.

3. Implement the ```rtc_auto.py``` host test script body according to your test flow (below is an existing example for RTC test):
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

3. Add ```rtc_auto.py``` to the mbed-host-tests module's registry under ```mbed-host-tests/mbed_host_tests/__init__.py```:
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
  * ```from host_tests.rtc_auto import RTCTest``` is used to import the ```rtc_auto.py``` script to this module.
  * ```HOSTREGISTRY.register_host_test("rtc_auto", RTCTest())``` is used to register the RTCTest() class implemented in ```rtc_auto.py``` under the name ```rtc_auto```.
    
    Note: ```rtc_auto``` is the same name that we are using in the test case C/C++ source code via the macro ```MBED_HOSTTEST_SELECT(rtc_auto);```.

4. (Re)install the mbed-host-tests module using the ```python setup.py install``` command in the cloned mbed-host-tests directory.
  * Note: the mbed-host-tests package should be installed on your system. Changes will take place only if you reinstall the package with your changes.

You can verify that your new host test is added to the mbed-host-test registry using the command:
```
$ mbedhtrun --list
```
```
'default'                 : mbed_host_tests.host_tests.default_auto.DefaultAuto()
'default_auto'            : mbed_host_tests.host_tests.default_auto.DefaultAuto()
'detect_auto'             : mbed_host_tests.host_tests.detect_auto.DetectPlatformTest()
'dev_null_auto'           : mbed_host_tests.host_tests.dev_null_auto.DevNullTest()
'echo'                    : mbed_host_tests.host_tests.echo.EchoTest()
'hello_auto'              : mbed_host_tests.host_tests.hello_auto.HelloTest()
'rtc_auto'                : mbed_host_tests.host_tests.rtc_auto.RTCTest()
'stdio_auto'              : mbed_host_tests.host_tests.stdio_auto.StdioTest()
'tcpecho_client_auto'     : mbed_host_tests.host_tests.tcpecho_client_auto.TCPEchoClientTest()
'tcpecho_client_ext_auto' : mbed_host_tests.host_tests.tcpecho_client_ext_auto.TCPServerEchoExtTest()
'tcpecho_server_auto'     : mbed_host_tests.host_tests.tcpecho_server_auto.TCPEchoServerTest()
'udpecho_client_auto'     : mbed_host_tests.host_tests.udpecho_client_auto.UDPEchoClientTest()
'udpecho_server_auto'     : mbed_host_tests.host_tests.udpecho_server_auto.UDPEchoServerTest()
'wait_us_auto'            : mbed_host_tests.host_tests.wait_us_auto.WaitusTest()
```
Here it is! :)
```
.
'rtc_auto'                : mbed_host_tests.host_tests.rtc_auto.RTCTest()
.
```

5. Use mbed-greenta to determine your platform's yotta target name (e.g. ```frdm-k64f-gcc```) using:
 ```
 $ mbedgt --config
 ```

6. Use mbed-greenta to build your test cases and execute them on the target:
  ```
  $ mbedgt --target=frdm-k64f-gcc
  ```

## Create a simple UT with CppUTest
In order to use the CppUTest library with your yotta package and test tools you need to include the dependency [mbed-cpputest-private](https://github.com/ARMmbed/mbed-cpputest-private), the mbed porting of CppUTest.
* This package contains the CppUTest library code (with useful UT macros).
* The additional source file [testrunner.cpp](https://github.com/ARMmbed/mbed-cpputest-private/blob/master/source/testrunner.cpp) is provided to guarantee correct implementation of the main() function.

  Note: in your unit test source code **please do not implement the ```main()``` function**. The ```main()``` function is already provided and is compatible with the existing tools.

  For example ```testrunner```'s ```main()``` function calls the proper macros for the handshake with the host test module.

To create this UT, first:

1. Create a new test case sub-directory and test source code under the ```\test``` directory.
2. Populate the test case's source code with the following template:
  ```c++
  #include <TestHarness.h>    // CppUTest stuff
  #include <mbed.h>
  
  TEST_GROUP(FirstTestGroup)
  {
  };
  
  TEST(FirstTestGroup, FirstTest)
  {
      /* These checks are here to make sure assertions outside test runs don't crash */
      CHECK(true);
      LONGS_EQUAL(1, 1);
      STRCMP_EQUAL("mbed SDK!", "mbed SDK!");
  }
  ```
3. Use the ```yotta build``` command to check if your test case compiles and builds before adding it to your yotta module.
4. Connect the mbed device to your computer (host) using USB.
5. Use mbed-greenta to determine your platform's yotta target name (e.g. ```frdm-k64f-gcc```) using:
 ```
 $ mbedgt --config
 ```

6. Use mbed-greenta to build test cases and execute them on the target:
  ```
  $ mbedgt --target=frdm-k64f-gcc
  ```

## More examples:
* You can refer to existing examples of tests in the [mbed-sdk-private](https://github.com/ARMmbed/mbed-sdk-private/tree/master/test) repository.
* All host tests with source code are [here](https://github.com/ARMmbed/mbed-host-tests/tree/master/mbed_host_tests/host_tests).

# Run mode. Running existing binaries with mbed-greentea
## Rationale
In some cases users only want to run prepared earlier binaries on target platform. For example users want to run demo application on target to make sure it works correctly. Below command allow users to execute binary on target and grab serial port output on console.

Command line option ```--run=<PATH_TO_FILE>``` allows users to specify path to existing binary which can be later on flashed and executed on target. Option ```-run``` should be combined with option ```--target``` so proper mbed platform type can be deduced.

## Example
Let's flash one of test binaries (remember you can flash any compatible with target binary) in run mode.
For this example we've connected one FRDM-K64F board to our host computer and we will use ```mbed-sdk``` yotta package as a rich source of test binaries.

* First we need to prepare binaries. We can use build ```mbed-sdk``` package effortlessly defining proper target for K64F platform and force ‘build only’ by specifying ```-O``` command line option
```
$ cd mbed-sdk
$ mbedgt --target=frdm-k64f-gcc -O
```

* Test binary will be a good example to flash and grab serial port output. We can list all test binaries’ names using ```--list``` command.
```
$ mbedgt --list
```
We should see something like this:
```
mbedgt: available tests for built targets
        location: 'c:\Work2\mbed-sdk-private\build'
target 'frdm-k64f-gcc':
        test 'mbed-test-eventhandler'
        test 'mbed-test-detect'
        test 'mbed-test-functionpointer'
        test 'mbed-test-div'
        test 'mbed-test-dev_null'
        test 'mbed-test-stl'
        test 'mbed-test-sleep_timeout'       
        test 'mbed-test-rtc'
        test 'mbed-test-hello'
        test 'mbed-test-stdio'
        test 'mbed-test-basic'

Example: execute 'mbedgt --target=TARGET_NAME -n TEST_NAME' to run TEST_NAME test only
```

* We can pick for example last test ```mbed-test-basic``` and just flash it (no test automation) to our target compatible device(s) connected to our host computer.
Binary should be located inside build directory. We can list it to make sure.
Note: We can specify path ot any binary compatible with our target, e.g. we can build example applciations inside our package and run them from ```.\build\TARGET\source``` folder or from build server if we are using this functionality in Continuous Integration pipeline.
```
$ ls .\build\frdm-k64f-gcc\test\mbed-test-basic.bin
.\build\frdm-k64f-gcc\test\mbed-test-basic.bin
```

* To run your binary and grab result please use following command:
```
$ mbedgt --target=frdm-k64f-gcc --run .\build\frdm-k64f-gcc\test\mbed-test-basic.bin
```
Where ```frdm-k64f-gcc``` is binary target and ```--run``` option specifies path to binary we want to execute.

Expected output:
```
yotta: search for existing mbed-target
mbedgt: current yotta target is: win,*
mbed-ls: detecting connected mbed-enabled devices...
        detected K64F, console at: COM61, mounted at: I:
mbedgt: scan available targets for 'K64F' platform...
yotta: search for mbed-target:k64f
        found target 'frdm-k64f-gcc'
        found target 'frdm-k64f-armcc'
mbed-host-test-runner: mbedhtrun -d I: -p COM61 -f ".\build\frdm-k64f-gcc\test\mbed-test-basic.bin" -C 4 -c shell -m K64F --run
MBED: Instrumentation: "COM61" and disk: "I:"
HOST: Copy image onto target...
        1 file(s) copied.
HOST: Initialize serial port...
...port ready!
HOST: Reset target...
{{timeout;20}}
{{host_test_name;default_auto}}
{{description;Basic}}
{{test_id;MBED_A1}}
{{start}}
{{success}}
{{end}}
mbed-host-test-runner: Stopped
```

Note: There is no way to determine if application executed on target finished executing. To prevent timout ```mbed-greentea``` exit please add print ```{{end}}``` at the end of your application execution. All tests ported to support ```mbed-greentea``` already print ```{{{end}}}``` tag so mbed-greentea exits after print is parsed. 
You can always stop mbed-greentea by pressing ```Ctrl+C```.

# Greentea Workflows
## Current configuration check
The following workflow shows the interaction between the test tools' components after a user calls the mbed-greentea command:
```
$ mbedgt --config
```
```
                                                              host OS             mbed device
                                                           =============          ===========
                                                                 | USB connection       |
                                                                 |<---------------------|
                                                                 |                      |
                                                                 | Mount serial         |
                                                                 |<---------------------|
                                                                 | Mount disk           |
                                                                 |<---------------------|
                 mbed-greentea                mbed-ls            |                      x
                 =============                =======            |
                       | Detect connected mbeds  |               |
                       |------------------------>| Detect dev.   |
                       |                         |<------------->|
                       | List of connected mbeds |               x
                       | List of avail. targets  |
                       |<------------------------|
                       |                         x
                       |
                       |
 yotta                 |
 =====                 |
   | yotta search      |
   |<------------------|
   |                   |
   | List of available |
   | targets for mbeds |
   |------------------>|
   x                   | Print configuration
                       |<-------------------
                       x
```
## Test build and execution workflow
The following workflow shows the interaction between the test tools' components after a user calls the mbed-greentea command:
```
$ mbedgt --target=<target_name>
```
```
                                                              host OS             mbed device
                                                           =============          ===========
                                                                 | USB connection       |
                                                                 |<---------------------|
                                                                 |                      |
                                                                 | Mount serial         |
                                                                 |<---------------------|
                                                                 | Mount disk           |
                                                                 |<---------------------|
                 mbed-greentea                mbed-ls            |                      |
                 =============                =======            |                      |
                       | Detect connected mbeds  |               |                      |
                       |------------------------>| Detect dev.   |                      |
                       |                         |<------------->|                      |
                       | List of connected mbeds |               x                      |
                       | List of avail. targets  |                                      |
                       |<------------------------|                                      |
                       |                         x                                      |
                       |                                                                |
                       |                                                                |
 yotta                 |                                                                |
 =====                 |                                                                |
   | Build target(s)   |                                                                |
   |<------------------|                                                                |
   |                   |                                                                |
   | Target(s) built   |                                                                |
   | Tests built       |                                                                |
   |------------------>|                                                                |
   x                   |                                                                |
                       |                                                                |
                       |                                                                |
            [For each test for mbed]                                                    |
                       |                                                                |
                       |                   mbed-host-tests                              |
                       |                   ===============                              |
                       | Test binary location     |                                     |
                       |------------------------->|                                     |
                       |                          | Flash test binary                   |
                       |                          |------------------------------------>|
                       |                          | Reset device                        |
                       |                          |------------------------------------>|
                       |                          |                                     |
                       |                          |                                     |
                       |                          | Serial port data connection         |
                       |                          | MBED_HOSTTEST_* macros handshake    |
                       |                          |<----------------------------------->|
                       |                          |                                     |
                       |                          | Host test HT_NAME is executed:      |
                       |                          | MBED_HOSTTEST_SELECT(HT_NAME)       |
                       |                          | and serial port handle belongs to   |
                       |                          | HT_NAME script.                     |
                       |                          |------------------------------------>|
                       |                          |                                     |
                       |                          | mbed dev. and HT_NAME script        |
                       |                          | interact and procude test result    |
                       |                          |<----------------------------------->|
                       |                          |                                     x
                       |                          |
                       |                          | Test result on serial, e.g. "{{success}}"
                       | Store test result        | Test end detected: "{{end}}"
                       |<-------------------------|<----------
                       |
                       |
                       | Print results
                       |<-------------
                       |
                 [For each end]
                       x
```
