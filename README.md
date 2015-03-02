# Introduction
Hello and welcome to the mbed SDK test suite, codename 'greentea'. 
The mbed test suite is a collection of tools that enable automated testing on mbed platforms.
The mbed test suite imports and uses following modules:

* [mbed-ls](https://github.com/ARMmbed/mbed-ls)
* [mbed-host-tests](https://github.com/ARMmbed/mbed-host-tests)

Make sure you've installed above Python modules. You can check it by typing:
```
pip freeze | grep mbed
mbed-greentea==0.0.5
mbed-host-tests==0.1.4
mbed-ls==0.1.5
```

Note: **At this current time, the test framework is targeted to run on Windows OS.**

## Supported mbed platforms
* [FRDM-K64F](http://developer.mbed.org/platforms/FRDM-K64F/).
* [NUCLEO_F401RE](http://developer.mbed.org/platforms/ST-Nucleo-F401RE/).

## Supported yotta targets
* ```frdm-k64f-gcc```.
* ```frdm-k64f-armcc```.
* ```st-nucleo-f401re-gcc```.

Note: More platforms and yotta targets will be added. In most cases only meta-data must be updated for each platform and target.

# Getting Started
To use the mbed test suite you must:
* Install the dependencies.
* Download and install the mbed test suite.
* Download mbed SDk sources.

## Dependencies
* [Python2.7](https://www.python.org/download/releases/2.7/) - all host side scripts are written in python
* [yotta](https://github.com/ARMmbed/yotta) - used to build tests from the mbed SDK
* [mbed-ls](https://github.com/ARMmbed/mbed-ls)
* [mbed-host-tests](https://github.com/ARMmbed/mbed-host-tests)
* Some Nucleo boards like F401RE can be correctly flashed only with ```cp``` or ```copy``` command line command. make sure in your system there is a ```cp``` shell command installed. It can be available by default (LInux OS) or provided by environments such as ```git```. We will assume you've installed ```git``` command line tools for Windows and ```cp``` command is available.

## Installation
To install the mbed test suite download the repo and run the setup.py script with the install option.
```
$ git clone https://github.com/ARMmbed/mbed-greentea.git
$ cd mbed-greentea
$ python setup.py install
```

Use the same procedure to install dependencies ```mbed-ls``` and ```mbed-host-tests```.

To check that the installer was successful try running the ```mbedgt --help``` command. You should get feedback like below. You may need to restart your terminal first.
```
$ mbedgt --help
Usage: mbedgt-script.py [options]

This automated test script is used to test mbed SDK 3.0 on mbed-enabled
deviecs with support from yotta build tool

Options:
  -h, --help            show this help message and exit
.
.
```

## Uninstall
You can unstall test suite package using ```pip```. List installed packages and filter for test suite package name:
```
$ pip freeze | grep mbed-greentea
mbed-greentea==0.0.5
```

Uninstall test suite package:
```
$ pip uninstall mbed-greentea
Uninstalling mbed-greentea:
  c:\python27\lib\site-packages\greentea-0.0.5-py2.7.egg
  c:\python27\scripts\mbedgt-script.py
  c:\python27\scripts\mbedgt.exe
  c:\python27\scripts\mbedgt.exe.manifest
Proceed (y/n)? Y
  Successfully uninstalled mbed-greentea
```

# Environment precheck
At this point you should install all dependencies and be ready to build mbed SDK and perform automated testing.
In current configuration mbed test suite can automatically detect most of popular mbed-enabled platforms connected to host via USB interface.

Test suite is using ```mbed-ls``` module to check connected devices and. Separate module called ```mbed-host –tests``` is used to flash and supervise each platforms test. This decoupling allows us to make better software and maintain each or the functionalities as separate domain. Previously mbed SDK test suite consisted of mentioned modules which is not good for maintainability and stopped us from building more efficient tools.

Make sure you have all tools installed. For example you can list all mbed devices connected to your host computer:
```
$ mbedls
+---------------------+-------------------+-------------------+--------------------------------+
|platform_name        |mount_point        |serial_port        |target_id                       |
+---------------------+-------------------+-------------------+--------------------------------+
|K64F                 |E:                 |COM61              |02400203D94B0E7724B7F3CF        |
|NUCLEO_F401RE        |F:                 |COM52              |07200200073E650A385BF317        |
+---------------------+-------------------+-------------------+--------------------------------+
```

# Testing
To test your platform you need to download mbed SDK sources and make sure you have mbed board (hardware) which is described and supported by any of available yotta modules.

First you can clone mbed SDK sources and move inside mbed SDK sources directory:
```
$ git clone https://github.com/ARMmbed/mbed-sdk.git
cd mbed-sdk
```
You are in mbed SDK directory and now you can execute test suite which will call yotta to build your sources first.

Let’s take one step back and see our current configuration:
```
$ mbedgt –config
mbed-ls: detecting connected mbed-enabled devices...
mbed-ls: detected K64F, console at: COM61, mounted at: E:
        got yotta target 'frdm-k64f-gcc'
        got yotta target 'frdm-k64f-armcc'
mbed-ls: detected NUCLEO_F401RE, console at: COM52, mounted at: F:
        got yotta target 'st-nucleo-f401re-gcc'
```
We can see ```mbedgt``` detected (using ```mbed-ls``` module) two boards connected to host system: ``` K64F```, ```NUCLEO_F401RE ```.

For each ```mbedgt``` proposed few supported yotta targets:
* ```frdm-k64f-gcc``` - Freescale K64F platform compiled with GCC cross-compiler.
* ```frdm-k64f-armcc``` - Freescale K64F platform compiled with Keil armcc cross-compiler.
* ```st-nucleo-f401re-gcc```- STMicro Nucleo F401RE platform compiled with GCC cross-compiler.

Because our test system doesn’t have Keil armcc compiler installed I will use only targets describing how to build mbed SDK using GCC cross-compiler. I want to build mbed SDK first to see if there are no issues. Let’s use test suite and invoke indirectly yotta to build only for two supported at this time targets.

In this example we will use option ````--target``` to specify targets I want to interact with. Option ```-O``` will be used to tell test suite to only build sources and tests without test procedure.

```
$ mbedgt --target=frdm-k64f-gcc,st-nucleo-f401re-gcc -O
mbed-ls: detecting connected mbed-enabled devices...
mbed-ls: detected K64F, console at: COM61, mounted at: E:
        got yotta target 'frdm-k64f-gcc'
mbed-ls: calling yotta to build your sources and tests
warning: uvisor-lib has invalid module.json:
warning:   author value [u'Milosch Meriac <milosch.meriac@arm.com>', u'Alessandro Angelino <alessandro.angelino@arm.com>'] is not valid under any of the given schemas
info: generate for target: frdm-k64f-gcc 0.0.10 at c:\temp\xxx\mbed-sdk-private\yotta_targets\frdm-k64f-gcc
mbedOS.cmake included
GCC-C.cmake included
mbedOS-GNU-C.cmake included
GCC-GXX.cmake included
mbedOS-GNU-CXX.cmake included
GCC version is: 4.8.4
GNU-ASM.cmake included
GNU-ASM.cmake included
-- Configuring done
-- Generating done
-- Build files have been written to: C:/temp/xxx/mbed-sdk-private/build/frdm-k64f-gcc
ninja: no work to do.
        got yotta target 'frdm-k64f-armcc'
mbed-ls: detected NUCLEO_F401RE, console at: COM52, mounted at: F:
        got yotta target 'st-nucleo-f401re-gcc'
mbed-ls: calling yotta to build your sources and tests
info: generate for target: st-nucleo-f401re-gcc 0.0.5 at c:\temp\xxx\mbed-sdk-private\yotta_targets\st-nucleo-f401re-gcc
mbedOS.cmake included
GCC-C.cmake included
mbedOS-GNU-C.cmake included
GCC-GXX.cmake included
mbedOS-GNU-CXX.cmake included
GCC version is: 4.8.4
GNU-ASM.cmake included
-- Configuring done
-- Generating done
-- Build files have been written to: C:/temp/xxx/mbed-sdk-private/build/st-nucleo-f401re-gcc
ninja: no work to do.
```

Now we know our sources and tests are built correctly. We can now call test suite again and ask for target test.

Please stay in the same directory (with mbed SDK) and execute below command:
```
mbedgt --target=frdm-k64f-gcc,st-nucleo-f401re-gcc
mbed-ls: detecting connected mbed-enabled devices...
mbed-ls: detected K64F, console at: COM61, mounted at: E:
        got yotta target 'frdm-k64f-gcc'
mbed-ls: calling yotta to build your sources and tests
warning: uvisor-lib has invalid module.json:
warning:   author value [u'Milosch Meriac <milosch.meriac@arm.com>', u'Alessandro Angelino <alessandro.angelino@arm.com>'] is not valid under any of the given schemas
info: generate for target: frdm-k64f-gcc 0.0.10 at c:\temp\xxx\mbed-sdk-private\yotta_targets\frdm-k64f-gcc
mbedOS.cmake included
GCC-C.cmake included
mbedOS-GNU-C.cmake included
GCC-GXX.cmake included
mbedOS-GNU-CXX.cmake included
GCC version is: 4.8.4
GNU-ASM.cmake included
GNU-ASM.cmake included
-- Configuring done
-- Generating done
-- Build files have been written to: C:/temp/xxx/mbed-sdk-private/build/frdm-k64f-gcc
ninja: no work to do.
mbedgt: running tests...
        test 'mbed-test-dev_null' .................................................... OK
        test 'mbed-test-cpp' ......................................................... OK
        test 'mbed-test-time_us' ..................................................... OK
        test 'mbed-test-ticker' ...................................................... OK
        test 'mbed-test-div' ......................................................... OK
        test 'mbed-test-detect' ...................................................... SKIPPED
        test 'mbed-test-call_before_main' ............................................ OK
        test 'mbed-test-basic' ....................................................... OK
        test 'mbed-test-stdio' ....................................................... OK
        test 'mbed-test-ticker_3' .................................................... OK
        test 'mbed-test-ticker_2' .................................................... OK
        test 'mbed-test-timeout' ..................................................... OK
        test 'mbed-test-rtc' ......................................................... OK
        test 'mbed-test-echo' ........................................................ OK
        test 'mbed-test-hello' ....................................................... OK
        got yotta target 'frdm-k64f-armcc'
mbed-ls: detected NUCLEO_F401RE, console at: COM52, mounted at: F:
        got yotta target 'st-nucleo-f401re-gcc'
mbed-ls: calling yotta to build your sources and tests
info: generate for target: st-nucleo-f401re-gcc 0.0.5 at c:\temp\xxx\mbed-sdk-private\yotta_targets\st-nucleo-f401re-gcc
mbedOS.cmake included
GCC-C.cmake included
mbedOS-GNU-C.cmake included
GCC-GXX.cmake included
mbedOS-GNU-CXX.cmake included
GCC version is: 4.8.4
GNU-ASM.cmake included
-- Configuring done
-- Generating done
-- Build files have been written to: C:/temp/xxx/mbed-sdk-private/build/st-nucleo-f401re-gcc
ninja: no work to do.
mbedgt: running tests...
        test 'mbed-test-dev_null' .................................................... OK
        test 'mbed-test-cpp' ......................................................... OK
        test 'mbed-test-time_us' ..................................................... OK
        test 'mbed-test-ticker' ...................................................... OK
        test 'mbed-test-div' ......................................................... OK
        test 'mbed-test-detect' ...................................................... SKIPPED
        test 'mbed-test-call_before_main' ............................................ OK
        test 'mbed-test-basic' ....................................................... OK
        test 'mbed-test-stdio' ....................................................... OK
        test 'mbed-test-ticker_3' .................................................... OK
        test 'mbed-test-ticker_2' .................................................... OK
        test 'mbed-test-timeout' ..................................................... OK
        test 'mbed-test-rtc' ......................................................... FAIL
        test 'mbed-test-echo' ........................................................ OK
        test 'mbed-test-hello' ....................................................... OK
```

# Common Issues
* Issue: In this release there are known issues related to Linux serial port handling during test.
  * Solution: Our army of cybernetic organisms is working on fix for this problem as we speak in your mind ;)
* Issue: Some boards show up as 'unknown'
  * Solution: we will add them in coming releases
* Issue: Not all mbed platforms have targets mapped to them.
  * Solution: Be patient, more target descriptions are comming.
