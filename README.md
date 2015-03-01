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

### Supported Platforms
* [FRDM-K64F](http://developer.mbed.org/platforms/FRDM-K64F/).
* [NUCLEO_F401RE](http://developer.mbed.org/platforms/ST-Nucleo-F401RE/).

### Supported yotta targets
* frdm-k64f-gcc
* frdm-k64f-armcc
* st-nucleo-f401re-gcc

Note: More platforms and yotta targets will be added. In most cases only meta-data must be updated for each platform and target.

# Getting Started
To use the mbed test suite you must:
* [Install the dependencies](#dependencies)
* [Download and install the mbed test suite](#installation)
* [Configure the test suite](#test-suite-configuration)

## Dependencies
* [Python2.7](https://www.python.org/download/releases/2.7/) - all host side scripts are written in python
* [yotta](https://github.com/ARMmbed/yotta) - used to build tests from the mbed SDK
* [mbed-ls](https://github.com/ARMmbed/mbed-ls)
* [mbed-host-tests](https://github.com/ARMmbed/mbed-host-tests)

## Installation
To install the mbed test suite download the repo and run the setup.py script with the install option.

```Shell
$ git clone https://github.com/ARMmbed/mbed-greentea.git
$ cd mbed-greentea
$ python setup.py install
```

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

### Uninstall
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


# Common Issues
* Issue: In this release there are known issues related to Linux serial port handling during test.
  * Solution: Our army of cybernetic organisms is working on fix for this problem as we speak in your mind ;)
* Issue: Some boards show up as 'unknown'
  * Solution: we will add them in coming releases
* Issue: 'mbed --tests' doesn't print anything
  * Solution: You either are not linking to the correct directory, or yotta didnt build any tests. 
