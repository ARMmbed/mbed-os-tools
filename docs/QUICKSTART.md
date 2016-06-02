# Table of content

* [Table of content](#table-of-content)
* [mbed test tools instructions](#mbed-test-tools-instructions)
  * [Limitations](#limitations)
  * [mbed test tools collection](#mbed-test-tools-collection)
  * [Dependencies check-list](#dependencies-check-list)
  * [Dependencies installation procedure](#dependencies-installation-procedure)
    * [Dependencies installation verification](#dependencies-installation-verification)
  * [Example test procedure walk-through](#example-test-procedure-walk-through)
* [Appendix A: (Optional) code coverage instrumentation](#appendix-a-optional-code-coverage-instrumentation)
  * [Prerequisites](#prerequisites)
  * [Code coverage measurement](#code-coverage-measurement)
* [Appendix B: (Optional) Installing mbed-ls tool](#appendix-b-optional-installing-mbed-ls-tool)

# mbed test tools instructions

This end to end example will guide you through the process of mbed test tools (_Greentea_) installation and use.

## Limitations

* ```Ubuntu```/```Linux```/```OSX```:
  * ```Greentea1``` mbed test tools work with _K64F's_ _DAPLink_ version _0240_ onwards.
  * See [Firmware FRDM K64F](https://developer.mbed.org/handbook/Firmware-FRDM-K64F) article for details how to update _DAPLink_ firmware to latest version.
    * Latest [DAPLink](https://github.com/mbedmicro/DAPLink) release can be found on [DAPLink release tab on GitHub](https://github.com/mbedmicro/DAPLink/releases).
  * You can check your _K64F_ device _DAPLink_ version with ```$ mbedls``` command (```daplink_version``` column). Please check [here](#appendix-b-optional-installing-mbed-ls-tool) how to install _mbed-ls_ tool.
  * Code coverage support (only for Ubuntu/Linux/OSX):
    * Works only for platforms natively supporting ```gcov``` and ```lcov``` applications.
* ```yotta test``` command may now work with mbed test tools 0.2.0 onwards.
  * Note: ```yotta test``` command is not part of this instructions.
  * We will fix that in the future.

## mbed test tools collection

mbed test tools set:
* [Greentea](https://github.com/ARMmbed/greentea) - mbed test automation framework, instrument test suite execution inside your yotta module.
  * This application is also distributed as Python Package: [mbed-greentea in PyPI](https://pypi.python.org/pypi/mbed-greentea).
* [greentea-client](https://github.com/ARMmbed/greentea-client) - ```Greentea``'s device side, C++ library.
  * This application is also distributed as yotta module: [greentea-client](https://yotta.mbed.com/#/module/greentea-client/0.1.8).
* [htrun](https://github.com/ARMmbed/htrun) - test runner for mbed test suite.
  * This application is also distributed as Python Package: [mbed-host-tests in PyPI](https://pypi.python.org/pypi/mbed-host-tests).
* [mbed-ls](https://github.com/ARMmbed/mbed-ls) - list all connected to host mbed compatible devices.
  * This application is also distributed as Python Package: [mbed-ls in PyPI](https://pypi.python.org/pypi/mbed-ls).

## Dependencies check-list

* Have one mbed board connected to your PC over USB. In our case it will be one [Freescale K64F](https://developer.mbed.org/platforms/FRDM-K64F/) board.
* Installed toolchain for ARM Cortex-M: [GCC ARM Embedded v4.9.3](https://launchpad.net/gcc-arm-embedded).
  * Note: ```arm-none-eabi-gcc``` and ```arm-none-eabi-g++``` must be added to system PATH.
* Installed ```git``` source control client: [Git](https://git-scm.com/downloads).
* Installed Python: [Python 2.7.11](https://www.python.org/download/releases/2.7/).
* Installed build tools: [yotta](https://github.com/ARMmbed/yotta):
* And of course installed _mbed test tools_: [Greentea](https://github.com/ARMmbed/greentea),  [htrun](https://github.com/ARMmbed/htrun) and [mbed-ls](https://github.com/ARMmbed/mbed-ls).
* You will need connection to Internet.

Next step will provide guidelines for _mbed test tools_ dependencies installation.

## Dependencies installation procedure

* Please install [Python 2.7.11](https://www.python.org/download/releases/2.7/). mbed test tools are not compatible with Python 3.x.
* Installed toolchain for ARM Cortex-M: [GCC ARM Embedded v4.9.3](https://launchpad.net/gcc-arm-embedded).
  * Note: ```arm-none-eabi-gcc``` and ```arm-none-eabi-g++``` must be added to system PATH.

You can check if you already have / correctly installed ARM toolchain by typing command:
```bash
$ arm-none-eabi-gcc --version
```
```bash
arm-none-eabi-gcc (GNU Tools for ARM Embedded Processors) 4.9.3 20150529 (release) [ARM/embedded-4_9-branch revision 227977]
Copyright (C) 2014 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

Note: We are currently supporting GNU Tools for ARM Embedded Processors version **4.9.x** (proffered version **4.9.3**).

* Please connect ```K64F``` to your host computer.
  * Make sure disk drive (MSD) and serial port (CDC) are all mounted and ready.
  * Have a look at [Configure mbed-enabled device to work with your host](https://github.com/ARMmbed/mbed-ls#configure-mbed-enabled-device-to-work-with-your-host) to resolve troubleshooting related to disk and serial port mount procedures.

* Installing ```yotta``` build system:
```
$ pip install yotta --upgrade
```
* Installing ```Greentea``` test automation tools:
```
$ pip install mbed-greentea --upgrade
```

* Check if ARM GCC Embedded toolchain _v4.9.3_ is installed:

```bash
$ arm-none-eabi-gcc --version
```
```bash
arm-none-eabi-gcc (GNU Tools for ARM Embedded Processors) 4.9.3 20150529 (release) [ARM/embedded-4_9-branch revision 227977]
Copyright (C) 2014 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

### Dependencies installation verification

* Check whether the mbed test tools dependencies exist on your machine:

```
$ pip freeze | grep mbed
```
```bash
mbed-greentea==0.2.6
mbed-host-tests==0.2.4
mbed-ls==0.2.1
```

* Check whether _yotta_ _v0.14.2_ was installed successfully:

```
$ yotta --version
```
```bash
0.14.2
```

* Check with _mbedls_ tool if your _K64F_ is detected correctly in the system:
```
$ mbedls
```
```
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| platform_name | platform_name_unique | mount_point | serial_port | target_id                                        | daplink_version |
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| K64F          | K64F[0]              | E:          | COM201      | 024002265f1b1e54000000000000000000000000a2c2e3ec | 0240            |
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
```

## Example test procedure walk-through

Test tools installation should be completed already. Now we will show how we can test ```mbed-drivers``` repository using ```Greentea``` automates test tools:

* Go to your working directory and clone ```mbed-drivers``` repository:
```bash
$ git clone https://github.com/ARMmbed/mbed-drivers.git
$ cd mbed-drivers
```

* Set the ```yotta``` build [target](http://yottadocs.mbed.com/tutorial/targets.html) to ```frdm-k64f-gcc```:
```bash
$ yotta target frdm-k64f-gcc
```
* Build the ```mbed-drivers``` module with yotta. ```Greentea``` can do this automatically for you but in our example we will use _yotta_ explicitly to build ```mbed-drivers``` repository sources:
```
$ yotta build
```
* ```Greentea``` command line tool is called ```mbedgt```. We can use it (with option ```--list``` / ```-l```) to list the built test cases:
```bash
$ mbedgt --list
mbedgt: available tests for built targets, location 'c:\Work\mbed-drivers\build'
        target 'frdm-k64f-gcc':
        test 'mbed-drivers-test-c_strings'
        test 'mbed-drivers-test-dev_null'
        test 'mbed-drivers-test-echo'
        test 'mbed-drivers-test-generic_tests'
        test 'mbed-drivers-test-rtc'
        test 'mbed-drivers-test-stl_features'
        test 'mbed-drivers-test-ticker'
        test 'mbed-drivers-test-ticker_2'
        test 'mbed-drivers-test-ticker_3'
        test 'mbed-drivers-test-timeout'
        test 'mbed-drivers-test-wait_us'
```

Above you can see list of tests (test suites) build with ```mbed-drivers``` repository. Tests are always located in ```test/``` sub-directory of every _yotta+ module. Each test suite is a separate binary. ```mbed-drivers``` module uses [utest](https://github.com/ARMmbed/utest) test harness to defines test cases inside test suite. ```utest``` is tightly coupled with ```Greentea``` mbed test tools providing robust test hardness solution. But enough about technical details...

```Greentea``` is a test automation tool which means it will for you detect connection to DUT (device under test), perform flashing operations for each test suite (binary with test case collection) and aggregate test suite / test case results in friendly human-readable report.

* Finally - tests execution:

Note:
a. ```mbedgt``` command line option ```-V``` is used to activate test case verbose mode.
b. ```mbedgt``` command line option ```-S``` is used to skip call to _yotta build_ command. We've already build ```mbed-drivers``` using command _yotta build_ so there is no need to invoke it again.
 c. Below command will execute for around _200 seconds_.

```
$ mbedgt -VS
...
[1458047568.17][HTST][INF] No events in queue
[1458047568.17][HTST][INF] stopped consuming events
[1458047568.17][HTST][INF] host test result() call skipped, received: True
[1458047568.17][HTST][WRN] missing __exit event from DUT
[1458047568.17][HTST][INF] calling blocking teardown()
[1458047568.17][HTST][INF] teardown() finished
[1458047568.17][HTST][INF] {{result;success}}
mbedgt: checking for GCOV data...
mbedgt: mbed-host-test-runner: stopped
mbedgt: mbed-host-test-runner: returned 'OK'
mbedgt: test on hardware with target id: 0240000033514e450041500585d40043e981000097969900
mbedgt: test suite 'mbed-drivers-test-ticker' ........................................................ OK in 21.20 sec
        test case: 'Timers: 2 x tickers' ............................................................. OK in 11.03 sec
mbedgt: test case summary: 1 pass, 0 failures
mbedgt: all tests finished!
mbedgt: shuffle seed: 0.3028454009
mbedgt: test suite report:
+---------------+---------------+---------------------------------+--------+--------------------+-------------+
| target        | platform_name | test suite                      | result | elapsed_time (sec) | copy_method |
+---------------+---------------+---------------------------------+--------+--------------------+-------------+
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | FAIL   | 12.77              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-dev_null      | OK     | 11.58              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-echo          | FAIL   | 19.96              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-generic_tests | OK     | 10.99              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-rtc           | OK     | 21.0               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stl_features  | OK     | 11.73              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker        | OK     | 21.2               | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker_2      | OK     | 21.18              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker_3      | OK     | 21.21              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-timeout       | OK     | 21.49              | shell       |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-wait_us       | OK     | 20.14              | shell       |
+---------------+---------------+---------------------------------+--------+--------------------+-------------+
mbedgt: test suite results: 2 FAIL / 9 OK
mbedgt: test case report:
+---------------+---------------+---------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| target        | platform_name | test suite                      | test case                           | passed | failed | result | elapsed_time (sec) |
+---------------+---------------+---------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %e %E float formatting   | 1      | 0      | OK     | 0.07               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %f %f float formatting   | 0      | 1      | FAIL   | 0.3                |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %g %g float formatting   | 1      | 0      | OK     | 0.06               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %i %d integer formatting | 1      | 0      | OK     | 0.06               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %u %d integer formatting | 1      | 0      | OK     | 0.06               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: %x %E integer formatting | 1      | 0      | OK     | 0.07               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: strpbrk                  | 1      | 0      | OK     | 0.04               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-c_strings     | C strings: strtok                   | 1      | 0      | OK     | 0.05               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-dev_null      | dev_null                            | 1      | 0      | OK     | 11.58              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-echo          | Echo server: x16                    | 1      | 0      | OK     | 1.6                |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-echo          | Echo server: x32                    | 0      | 0      | ERROR  | 0.0                |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-generic_tests | Basic                               | 1      | 0      | OK     | 0.03               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-generic_tests | Blinky                              | 1      | 0      | OK     | 0.04               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-generic_tests | C++ heap                            | 1      | 0      | OK     | 0.1                |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-generic_tests | C++ stack                           | 1      | 0      | OK     | 0.15               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-rtc           | RTC strftime                        | 1      | 0      | OK     | 10.43              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stl_features  | STL std::equal                      | 1      | 0      | OK     | 0.04               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stl_features  | STL std::sort abs                   | 1      | 0      | OK     | 0.03               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stl_features  | STL std::sort greater               | 1      | 0      | OK     | 0.05               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-stl_features  | STL std::transform                  | 1      | 0      | OK     | 0.05               |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker        | Timers: 2 x tickers                 | 1      | 0      | OK     | 11.03              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker_2      | Timers: 1x ticker                   | 1      | 0      | OK     | 11.04              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-ticker_3      | Timers: 2x callbacks                | 1      | 0      | OK     | 11.04              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-timeout       | Timers: toggle on/off               | 1      | 0      | OK     | 11.25              |
| frdm-k64f-gcc | K64F          | mbed-drivers-test-wait_us       | Timers: wait_us                     | 1      | 0      | OK     | 10.05              |
+---------------+---------------+---------------------------------+-------------------------------------+--------+--------+--------+--------------------+
mbedgt: test case results: 1 FAIL / 23 OK / 1 ERROR
mbedgt: completed in 194.37 sec
mbedgt: exited with code 2
```

Above report shows test suite / test case result report. ```Greetea``` is tool designed to work in continuous Integration environment so its return code to environment is non-zero (in this case ```2```) because not all tests passed (1 FAIL, 1 ERROR).

* You can repeat this procedure for each core mbed repository. For example you can clone one of:
  * [core-util](https://github.com/ARMmbed/core-util),
  * [ualloc](https://github.com/ARMmbed/ualloc),
  * [minar](https://github.com/ARMmbed/minar),
  * [utest](https://github.com/ARMmbed/utest) or
  * [mbed-drivers](https://github.com/ARMmbed/mbed-drivers) (already tested by us in this example).

# Appendix A: (Optional) code coverage instrumentation

* This is **optional procedure** introduced with latest test tools.
* For those who are using Ubuntu/Linux/OSX OSs it is possible to run code coverage metrics on ```mbed-drivers``` test code we've just executed.
* The same procedure applies for all core mbed modules with tests.

## Prerequisites

* Code coverage instrumentation only works on Ubuntu/Linux/OSX hosts.
* You have installed [gcov](https://gcc.gnu.org/onlinedocs/gcc-4.5.3/gcc/Gcov-Intro.html#Gcov-Intro) and [LCOV](http://ltp.sourceforge.net/coverage/lcov.php) tools. You can check below in you already have installed this tools:

```bash
$ gcov --version
```
```bash
gcov (Ubuntu 4.8.4-2ubuntu1~14.04.1) 4.8.4
Copyright (C) 2013 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.
There is NO warranty; not even for MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.
```
```bash
$ lcov --version
```
```bash
lcov: LCOV version 1.10
```

* You need to make sure you are using GCC ARM Embedded toolchain version **4.9.3**.
* We will have to create two additional files in root directory of ```mbed-drivers``` and rebuild our project.

## Code coverage measurement

* Make sure your _K64F_ is plugged in.
* Make sure you are in ```./mbed-drivers``` directory.

* Create in root directory of previously cloned ```mbed-drivers``` repository file ```config.json``` with content:

```json
{
    "debug":{
        "options" : {
            "coverage" : {
                "modules" : {
                    "mbed-drivers" : true
                }
            }
        }
    },
    "mbed-os": {
      "stdio": {
        "default-baud": 115200
    }
  }
}
```

* Create in root directory of previously cloned ```mbed-drivers``` repository file ```lcovhooks.json``` with content:

```json
{
    "hooks": {
        "hook_test_end": "$lcov --gcov-tool arm-none-eabi-gcov  --capture --directory ./build --output-file ./build/{yotta_target_name}/{test_name}.info",
        "hook_post_all_test_end": "$lcov --gcov-tool arm-none-eabi-gcov [-a ./build/{yotta_target_name}/{test_name_list}.info] --output-file result.info"
    }
}
```

* Rebuild your ```mbed-drivers``` project with new configuration supporting code coverage:

```bash
$ yotta build --config config.json
```

* Re-run ```mbedgt``` this time with code coverage hooks which will instrument LCOV to merge and generate code coverage support:

```bash
$ mbedgt -VS -H lcovhooks.json
```
```
...
mbedgt: hook 'hook_post_all_test_end' execution
        hook command: lcov --gcov-tool arm-none-eabi-gcov -a ./build/frdm-k64f-gcc/mbed-drivers-test-c_strings.info -a ./build/frdm-k64f-gcc/mbed-drivers-test-dev_null.info -a ./build/frdm-k64f-gcc/mbed-drivers-test-echo.info -a ./build/frdm-k64f-gcc/mbed-drivers-test-generic_tests.info -a ./build/frdm-k64f-gcc/mbed-drivers-test-rtc.info -a ./build/frdm-k64f-gcc/mbed-drivers-test-stl_features.info -a ./build/frdm-k64f-gcc/mbed-drivers-test-ticker.info -a ./build/frdm-k64f-gcc/mbed-drivers-test-ticker_2.info -a ./build/frdm-k64f-gcc/mbed-drivers-test-ticker_3.info -a ./build/frdm-k64f-gcc/mbed-drivers-test-timeout.info -a ./build/frdm-k64f-gcc/mbed-drivers-test-wait_us.info --output-file result.info
Combining tracefiles.
Reading tracefile ./build/frdm-k64f-gcc/mbed-drivers-test-c_strings.info
Reading tracefile ./build/frdm-k64f-gcc/mbed-drivers-test-dev_null.info
Reading tracefile ./build/frdm-k64f-gcc/mbed-drivers-test-echo.info
Reading tracefile ./build/frdm-k64f-gcc/mbed-drivers-test-generic_tests.info
Reading tracefile ./build/frdm-k64f-gcc/mbed-drivers-test-rtc.info
Reading tracefile ./build/frdm-k64f-gcc/mbed-drivers-test-stl_features.info
Reading tracefile ./build/frdm-k64f-gcc/mbed-drivers-test-ticker.info
Reading tracefile ./build/frdm-k64f-gcc/mbed-drivers-test-ticker_2.info
Reading tracefile ./build/frdm-k64f-gcc/mbed-drivers-test-ticker_3.info
Reading tracefile ./build/frdm-k64f-gcc/mbed-drivers-test-timeout.info
Reading tracefile ./build/frdm-k64f-gcc/mbed-drivers-test-wait_us.info
Writing data to result.info
Summary coverage rate:
  lines......: 43.0% (312 of 725 lines)
  functions..: 36.3% (70 of 193 functions)
  branches...: no data found
...
mbedgt: test case results: 1 FAIL / 23 OK / 1 ERROR
mbedgt: completed in 230.66 sec
mbedgt: exited with code 2
```

* After procedure is completed you can use LCOV to generate HTML code coverage report to directory ```./htmlcov/```:

```bash
$ genhtml result.info --output-directory htmlcov/
```
```bash
Reading data file result.info
Found 38 entries.
Found common filename prefix "/home/przemek/devel_transport/mbed-drivers"
Writing .css and .png files.
Generating output.
Processing file mbed-drivers/SerialBase.h
Processing file mbed-drivers/CThunk.h
Processing file mbed-drivers/Transaction.h
Processing file mbed-drivers/FileHandle.h
Processing file mbed-drivers/Buffer.h
Processing file mbed-drivers/Serial.h
Processing file mbed-drivers/Ticker.h
Processing file mbed-drivers/DirHandle.h
Processing file mbed-drivers/Timeout.h
Processing file mbed-drivers/FileSystemLike.h
Processing file source/rtc_time.c
Processing file source/FileBase.cpp
Processing file source/Ticker.cpp
Processing file source/TimerEvent.cpp
Processing file source/us_ticker_api.c
Processing file source/exit.c
Processing file source/pinmap_common.c
Processing file source/FileSystemLike.cpp
Processing file source/Stream.cpp
Processing file source/Timeout.cpp
Processing file source/SerialBase.cpp
Processing file source/wait_api.c
Processing file source/retarget.cpp
Processing file source/ticker_api.c
Processing file source/gpio.c
Processing file source/error.c
Processing file source/Serial.cpp
Processing file source/board.c
Processing file source/FileLike.cpp
Processing file source/FilePath.cpp
Processing file yotta_modules/cmsis-core/cmsis-core/core_cmFunc.h
Processing file yotta_modules/cmsis-core/cmsis-core/core_cmInstr.h
Processing file yotta_modules/core-util/core-util/FunctionPointerBind.h
Processing file yotta_modules/core-util/core-util/FunctionPointerBase.h
Processing file yotta_modules/core-util/core-util/FunctionPointer.h
Processing file yotta_modules/mbed-hal-ksdk-mcu/mbed-hal-ksdk-mcu/gpio_object.h
Processing file /usr/arm-none-eabi/include/time.h
Processing file /usr/arm-none-eabi/include/stdlib.h
Writing directory view page.
Overall coverage rate:
  lines......: 43.0% (312 of 725 lines)
  functions..: 36.3% (70 of 193 functions)
```

* Open with web browser file ```./htmlcov/index.html``` to get access to code coverage report in HTML format.

```
$ cat htmlcov/index.html
```
```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">

<html lang="en">

<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>LCOV - result.info</title>
  <link rel="stylesheet" type="text/css" href="gcov.css">
</head>
...
```

# Appendix B: (Optional) Installing mbed-ls tool

[mbed-ls](https://github.com/ARMmbed/mbed-ls)  is a Python module that detects and lists mbed-enabled devices connected to the host computer. You may want to install _mbed-ls_ on your system before you start further.
Please follow [mbed-ls installation](https://github.com/ARMmbed/mbed-ls#installation) instructions to install _mbed-ls_.

Note: After installation of _mbed-ls_ tool you will have to your disposal command line application ```mbedls```.

```
$ mbedls
+---------------+----------------------+-------------+-------------+---------------------------+-----------------+
| platform_name | platform_name_unique | mount_point | serial_port | target_id                 | daplink_version |
+---------------+----------------------+-------------+-------------+---------------------------+-----------------+
| K64F          | K64F[0]              | E:          | COM201      | 024002265f1b1e540a2c2e3ec | 0240            |
+---------------+----------------------+-------------+-------------+---------------------------+-----------------+
```
