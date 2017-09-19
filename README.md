[![Build status](https://circleci.com/gh/ARMmbed/mbed-ls/tree/master.svg?style=svg)](https://circleci.com/gh/ARMmbed/mbed-ls/tree/master)
[![Coverage Status](https://coveralls.io/repos/github/ARMmbed/mbed-ls/badge.svg?branch=master)](https://coveralls.io/github/ARMmbed/mbed-ls?branch=master)
[![PyPI version](https://badge.fury.io/py/mbed-ls.svg)](https://badge.fury.io/py/mbed-ls)

# Table of contents

* [Description](#description)
* [Rationale](#rationale)
* [Installation](#installation)
  * [Installation from PyPI (Python Package Index)](#installation-from-pypi-python-package-index)
  * [Installation from Python sources](#installation-from-python-sources)
* [mbedls as command line tool](#mbedls-as-command-line-tool)
  * [Exporting mbedls output to JSON](#exporting-mbedls-output-to-json)
* [Porting instructions](#porting-instructions)
  * [mbed-enabled technical specification overview](#mbed-enabled-technical-specification-overview)
    * [TargetID as device unique identifier](#targetid-as-device-unique-identifier)
  * [mbed-ls auto-detection approach for Ubuntu](#mbed-ls-auto-detection-approach-for-ubuntu)
* [Retarget mbed-ls autodetection results](#retarget-mbed-ls-autodetection-results)
  * [mbedls.json file properties](#mbedlsjson-file-properties)
  * [Example of retargeting](#example-of-retargeting)
* [Mocking new or existing target to custom platform name](#mocking-new-or-existing-target-to-custom-platform-name)
  * [Mock command line examples](#mock-command-line-examples)
  * [Mocking example with Freescale K64F platform](#mocking-example-with-freescale-k64f-platform)
* [mbed-ls unit testing](#mbed-ls-unit-testing)
  * [Code coverage](#code-coverage)
* [Configure mbed-enabled device to work with your host](#configure-mbed-enabled-device-to-work-with-your-host)
  * [Windows serial port configuration](#windows-serial-port-configuration)
  * [Mounting with sync](#mounting-with-sync)
    * [Ubuntu](#ubuntu)
  * [Raspberry Pi - Raspbian Jessie Lite](#raspberry-pi---raspbian-jessie-lite)
    * [Prerequisites](#prerequisites)
    * [Install LDM](#install-ldm)
    * [Enable LDM](#enable-ldm)
    * [Making sure LDM is active (running)](#making-sure-ldm-is-active-running)
* [Known issues](#known-issues)

# Description

```mbed-ls``` is a Python (2 and 3) module that detects and lists mbed-enabled devices connected to the host computer. It will be delivered as a redistributable Python module (package) and command line tool.

Currently supported operating system:

* Windows 7.
* Linux.
* Mac OS X (Darwin).
* Raspbian Jessie Lite.

# Rationale

When connecting more than one mbed-enabled device to the host computer, it takes time to manually check the platforms' binds:

* Mount point (MSD / disk).
* Virtual serial port (CDC).
* mbed's TargetID and generic platform name.

```mbed-ls``` provides these points of information for all connected boards at once in a simple console (terminal) output.

# Installation

## Installation from PyPI (Python Package Index)

mbed-ls module is redistributed via PyPI. We recommend you use the [application pip](https://pip.pypa.io/en/latest/installing.html#install-pip).

**Note:** Python 2.7.9 onwards include ```pip``` by default, so you may have ```pip``` already.

To install mbed-ls from [PyPI](https://pypi.python.org/pypi/mbed-ls) use command:
```
$ pip install mbed-ls --upgrade
```

## Installation from Python sources

**Prerequisites:** you need to have [Python 2.7.x](https://www.python.org/download/releases/2.7/) or [Python 3.6.x](https://www.python.org/downloads/release/python-362/) installed on your system.

**Note:** if your OS is Windows, please follow the installation instructions [for the serial port driver](https://developer.mbed.org/handbook/Windows-serial-configuration).

To install the mbed-ls module:

Clone the mbed-ls repository. The following example uses the GitHub command line tools, but you can do this directly from the website:

```
$ git clone https://github.com/ARMmbed/mbed-ls.git
```

Change the directory to the mbed-ls repository directory:

```
$ cd mbed-ls
```

Now you are ready to install mbed-ls.

```
$ python setup.py install
```

On Linux, if you have a problem with permissions please try to use ```sudo```:

```
$ sudo python setup.py install
```

The above command should install the ```mbed-ls``` Python package (import ```mbed_lstools```) and mbedls command.

To test if your installation succeeded try the ```mbedls``` command:

```
$ mbedls
```

Or use the Python interpreter and import ```mbed_lstools```:

```
$ python
Python 2.7.8 (default, Jun 30 2014, 16:03:49) [MSC v.1500 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
```

Generic mbedls API example:
```python
>>> import mbed_lstools
>>> mbeds = mbed_lstools.create()
>>> mbeds
<mbed_lstools.lstools_win7.MbedLsToolsWin7 instance at 0x02F542B0>
>>> mbeds.list_mbeds()
[{'platform_name': 'K64F', 'mount_point': 'E:', 'target_id': '02400203D94B0E7724B7F3CF', 'serial_port': u'COM61'}]
>>> print mbeds
```

Extended mbedls API example:
```python
>>> import mbed_lstools
>>> m = mbed_lstools.create()
>>> dir(m)
['DEBUG_FLAG',
 'ERRORLEVEL_FLAG',
 '__doc__',
 '__init__',
 '__module__',
 '__str__',
 'debug',
 'discover_connected_mbeds',
 'err',
 'get_connected_mbeds',
 'get_dos_devices',
 'get_json_data_from_file',
 'get_mbed_com_port',
 'get_mbed_devices',
 'get_mbed_htm_target_id',
 'get_mbeds',
 'get_mounted_devices',
 'get_string',
 'iter_keys',
 'iter_keys_as_str',
 'iter_vals', 'list_mbeds',
 'list_mbeds_by_targetid',
 'list_mbeds_ext',
 'list_platforms',
 'list_platforms_ext',
 'load_mbed_description',
 'manufacture_ids',
 'os_supported',
 'regbin2str',
 'scan_html_line_for_target_id',
 'usb_vendor_list',
 'winreg']
>>> m.list_platforms()
['LPC1768', 'K64F']
>>> m.list_platforms_ext()
{'K64F': 1, 'LPC1768': 2}
```

# mbedls as command line tool

After installation of the mbed-ls package, you can use the mbedls command. It allows you to list all connected mbed-enabled devices and gives you the correct association between your board mount point (disk) and the serial port. TargetID information is also provided for your information.

```
$ mbedls
+---------------------+-------------------+-------------------+--------------------------------+
|platform_name        |mount_point        |serial_port        |target_id                       |
+---------------------+-------------------+-------------------+--------------------------------+
|KL25Z                |I:                 |COM89              |02000203240881BBD9F47C43        |
|NUCLEO_F302R8        |E:                 |COM34              |07050200623B61125D5EF72A        |
+---------------------+-------------------+-------------------+--------------------------------+
```

If you want to use ```mbedls``` in your toolchain, continuous integration or automation script and do not necessarily want to use the Python module ```mbed_lstools``` - this solution is for you.

On some Linux systems, USB mass storage devices are not automatically mounted and do not show up when running `mbedls` by default. If you would like to include these not mounted devices in `mbedls` output, you can run mbed-ls with the `-u` option, such as `$ mbedls -u`.

## Exporting mbedls output to JSON

You can export mbedls outputs to JSON format: just use the ```---json``` switch and dump your file on the screen or redirect to a file. It should help you further automate your processes.

```json
$ mbedls --json
[
    {
        "mount_point": "E:",
        "platform_name": "NUCLEO_L152RE",
        "serial_port": "COM9",
        "target_id": "07100200860579FAB960EFD7"
    },
    {
        "mount_point": "F:",
        "platform_name": null,
        "serial_port": "COM5",
        "target_id": "A000000001"
    },
    {
        "mount_point": "G:",
        "platform_name": "NUCLEO_F302R8",
        "serial_port": "COM34",
        "target_id": "07050200623B61125D5EF72A"
    },
    {
        "mount_point": "H:",
        "platform_name": "LPC1768",
        "serial_port": "COM77",
        "target_id": "101000000000000000000002F7F18695"
    },
    {
        "mount_point": "I:",
        "platform_name": "KL25Z",
        "serial_port": "COM89",
        "target_id": "02000203240881BBD9F47C43"
    }
]
```

# Porting instructions

You can help us improve the mbed-ls tools by - for example - committing a new OS port. You can see the list of currently supported OSs in the [Description](#description) section; if your OS isn't there, you can port it.

For further study please check how Mac OS X (Darwin) was ported in [this pull request](https://github.com/ARMmbed/mbed-ls/pull/1).

## mbed-enabled technical specification overview

[mbed-enabled](https://www.mbed.com/en/about-mbed/mbed-enabled/) program is designed for mbed developers and partners who want to clearly identify their products as interoperable mbed Enabled technologies.
User facing [DAPLink](https://github.com/mbedmicro/DAPLink#daplink) interface connects mbed-enabled device with host computer using USB interface.

Interface chip should in general follow few generic rules to allow proper host detection and compliance with for example mbed test tools. There are listed below:
* Existance of CDC (virtual serial port)
  * Must support at all standard baudrates 9600 thru 115200
  * Must Support `SendBreak` resulting in target reset sequence
  * MUst have TargetID embedded in USBID
* Mass Storage Device Class
  * Must support programming binary files (copy file on MSD results in target flashing)
  * Target flashing should not result in automatic target reset
  * Must have `DETAILS.TXT` with DAPlink specification
  * Must have `mbed.htm` with DAPlink specification
  * `mbed.htm` should contain link to platform with `TargetID` specified
  * Must have TargetID embedded in `USBID`

### TargetID as device unique identifier

Each device must have an unique identifier which generic format is specified in below chapter.

TargetID generic format:
* ASCII string containing hexadecimal values only: `[a-fA-F0-9]{4, }`
* Should be longer than four ASCII characters (two bytes of hex data)
* First 2 bytes coded with four ASCII characters are `vendor code`
    * Note: *There might be more than one vendor code value assigned to one vendor.*
* Following 2 bytes coded with four ASCII characters are `platform code`*
* Rest of ASCII characters are vendor / platform specific. Ignored by mbed-enabled tools
* `Vendor code` + `platform code` should create globally unique value

Example TargetID coding:
* Freescale `K64F` TargetID: `0240000033514e450019500585d40008e981000097969900`

```
        02	40	000033514e450019500585d40008e981000097969900
        |   |
        |   v
        v	K64F
        Freescale
```

## mbed-ls auto-detection approach for Ubuntu

Let's connect a few mbed boards to our Ubuntu host. The devices should mount as MSC and CDC (virtual disk and serial port). We'll use regular Linux commands to see the boards, then see how ```mbed-ls``` displays them.

In this example, we've connected to our Ububtu machine's USB ports:

* 2 x STMicro's Nucleo mbed boards.
* 2 x NXP mbed boards.
* 1 x Freescale Freedom board.

We can see the mounting result in the usb-id directories in Ubuntu's file system under ```/dev/```. To list mbed boards mounted to serial ports (CDC) via USB, we use the general Linux command:

```
$ ll /dev/serial/by-id
```

We'll see:

```
total 0
drwxr-xr-x root 140 Feb 19 12:38 ./
drwxr-xr-x root  80 Feb 19 12:35 ../
lrwxrwxrwx root  13 Feb 19 12:38 usb-MBED_MBED_CMSIS-DAP_02000203240881BBD9F47C43-if01 -> ../../ttyACM0
lrwxrwxrwx root  13 Feb 19 12:35 usb-MBED_MBED_CMSIS-DAP_A000000001-if01 -> ../../ttyACM4
lrwxrwxrwx root  13 Feb 19 12:35 usb-mbed_Microcontroller_101000000000000000000002F7F18695-if01 -> ../../ttyACM3
lrwxrwxrwx root  13 Feb 19 12:35 usb-STMicroelectronics_STM32_STLink_066EFF525257775087141721-if02 -> ../../ttyACM2
lrwxrwxrwx root  13 Feb 19 12:35 usb-STMicroelectronics_STM32_STLink_066EFF534951775087215736-if02 -> ../../ttyACM1
```

To list boards mounted to disks (MSC) via USB, we use the general Linux command:
```
$ ll /dev/disk/by-id
```

We'll see:

```
total 0
drwxr-xr-x root 340 Feb 19 12:38 ./
drwxr-xr-x root 120 Feb 19 12:35 ../
lrwxrwxrwx root   9 Dec  3 09:10 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM -> ../../sda
lrwxrwxrwx root  10 Dec  3 09:10 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part1 -> ../../sda1
lrwxrwxrwx root  10 Dec  3 09:10 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part2 -> ../../sda2
lrwxrwxrwx root  10 Dec  3 09:10 ata-HDS728080PLA380_40Y9028LEN_PFDB32S7S44XLM-part5 -> ../../sda5
lrwxrwxrwx root   9 Dec  3 09:10 ata-TSSTcorpDVD-ROM_TS-H352C -> ../../sr0
lrwxrwxrwx root   9 Feb 19 12:35 usb-MBED_MBED_CMSIS-DAP_A000000001-0:0 -> ../../sdf
lrwxrwxrwx root   9 Feb 19 12:38 usb-MBED_microcontroller_02000203240881BBD9F47C43-0:0 -> ../../sdb
lrwxrwxrwx root   9 Feb 19 12:35 usb-MBED_microcontroller_066EFF525257775087141721-0:0 -> ../../sdd
lrwxrwxrwx root   9 Feb 19 12:35 usb-MBED_microcontroller_066EFF534951775087215736-0:0 -> ../../sdc
lrwxrwxrwx root   9 Dec  3 16:10 usb-MBED_microcontroller_0670FF494956805087154420-0:0 -> ../../sdc
lrwxrwxrwx root   9 Feb 19 12:35 usb-mbed_Microcontroller_101000000000000000000002F7F18695-0:0 -> ../../sde
lrwxrwxrwx root   9 Dec  3 09:10 wwn-0x5000cca30ccffb77 -> ../../sda
lrwxrwxrwx root  10 Dec  3 09:10 wwn-0x5000cca30ccffb77-part1 -> ../../sda1
lrwxrwxrwx root  10 Dec  3 09:10 wwn-0x5000cca30ccffb77-part2 -> ../../sda2
lrwxrwxrwx root  10 Dec  3 09:10 wwn-0x5000cca30ccffb77-part5 -> ../../sda5
```

***Note:*** ```mbed-ls``` tools pair only serial ports and mount points (not CMSIS-DAP - yet).

We can see that on our host machine (running Ubuntu) there are many 'disk type' devices visible under ```/dev/disk```. The mbed boards can be distinguished and filtered by their unique ```USB-ID``` conventions. In our case, we can see pairs of ```usb-ids``` in both ```/dev/serial/usb-id``` and ```/dev/disk/usb-id``` with embedded ``` TargetID```.  ```TargetID``` can be filtered out, for example using this sudo-regexpr: ```(“MBED”|”mbed”|”STMicro”)_([a-zA-z_-]+)_([a-zA-Z0-9]){4,}```

For example, we can match the board 066EFF525257775087141721 by connecting a few dots:

* ```usb-MBED_microcontroller_066EFF525257775087141721-0:0 -> ../../sdd```
* ```usb-STMicroelectronics_STM32_STLink_066EFF525257775087141721-if02 -> ../../ttyACM2``` Based on the TargetID hash.

From this we know that the target platform has these properties:

* The unique target platform identifier is ```066E```.
* The serial port is ```ttyACM2```.
* The mount point is ```sdd```.

Your ```mbed-ls``` implementation resolves those three and creates a “tuple” with those values (for each connected device). Using this tuple(s), ```mbed-ls``` will convert the platform number to a human-readable name etc.

Note that for some boards the ```TargetID``` format is proprietary (see STMicro boards) and ```usb-id``` does not have a valid TargetID where the four first letters are the target platform's unique ID. In that case, ```mbed-ls``` tools inspects the ```mbed.htm``` file on the mbed mounted disk to get the proper TargetID from the URL in the ```meta``` part of the HTML header.

In the following example, the URL ```http://mbed.org/device/?code=07050200623B61125D5EF72A``` for the STMicro Nucleo F302R8 board contains the valid TargetID ```07050200623B61125D5EF72A```, which ```mbed-ls``` uses to detect the ```platform_name```. ```mbed-ls``` will then replace the invalid TargetID in ```usb-id``` with the value from ```mbed.htm```.

```html
<!-- mbed Microcontroller Website and Authentication Shortcut -->
<!-- Version: 0200 Build: Aug 27 2014 13:29:28 -->
<html>
<head>
<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code=07050200623B61125D5EF72A"/>
<title>mbed Website Shortcut</title>
</head>
<body></body>
</html>
```

This is the result of ```mbedls``` listing the connected devices that we saw above:
```
$ mbedls
+---------------------+-------------------+-------------------+----------------------------------------+
|platform_name        |mount_point        |serial_port        |target_id                               |
+---------------------+-------------------+-------------------+----------------------------------------+
|KL25Z                |I:                 |COM89              |02000203240881BBD9F47C43                |
|LPC1768              |H:                 |COM77              |101000000000000000000002F7F18695        |
|NUCLEO_F302R8        |G:                 |COM34              |07050200623B61125D5EF72A                |
|NUCLEO_L152RE        |E:                 |COM9               |07100200860579FAB960EFD7                |
|unknown              |F:                 |COM5               |A000000001                              |
+---------------------+-------------------+-------------------+----------------------------------------+
```

# Retarget mbed-ls autodetection results

User can create file ```mbedls.json``` in given directory. ```mbedls.json``` file should contain JSON formatted data which will redefine mbed's parameters returned by mbed-ls. ```mbed-ls``` will automatically read ```mbedls.json``` file and alter auto-detection result.
File should be placed in directory where we want to alter mbed-ls behavior.

* Note: This feature in implicitly ON.
* Note: This feature can be turned off with command line switch ```--skip-retarget```.

## mbedls.json file properties
* If file ```mbedls.json``` exists will be implicitly used to retarget results.
* If file ```mbedls.json``` exists and flag ```--skip-retarget``` is set, there will be no retarget.
* If file ```mbedls.json``` doesn't exist flag ```--skip-retarget``` has no effect.

## Example of retargeting
In this example we will replace serial port name during Freescale's K64F auto-detection:
```
$ mbedls
+--------------+---------------------+------------+------------+-------------------------------------------------+
|platform_name |platform_name_unique |mount_point |serial_port |target_id                                        |
+--------------+---------------------+------------+------------+-------------------------------------------------+
|K64F          |K64F[0]              |F:          |COM9        |0240022648cb1e77000000000000000000000000b512e3cf |
+--------------+---------------------+------------+------------+-------------------------------------------------+
```

Our device is detected on port ```COM9``` and MSD is mounted on ```F:```. We can check more details using ```--json``` switch:
```
$ mbedls --json
[
    {
        "mount_point": "F:",
        "platform_name": "K64F",
        "platform_name_unique": "K64F[0]",
        "serial_port": "COM9",
        "target_id": "0240022648cb1e77000000000000000000000000b512e3cf",
        "target_id_mbed_htm": "0240022648cb1e77000000000000000000000000b512e3cf",
        "target_id_usb_id": "0240022648cb1e77000000000000000000000000b512e3cf"
    }
]
```

We must understand that ```mbed-ls``` stores information about mbed devices in dictionaries.
The same information can be presented as dictionary where its keys are ```target_id``` and value is a mbed auto-detection data.

```
$ mbedls --json-by-target-id
{
    "0240022648cb1e77000000000000000000000000b512e3cf": {
        "mount_point": "F:",
        "platform_name": "K64F",
        "platform_name_unique": "K64F[0]",
        "serial_port": "COM9",
        "target_id": "0240022648cb1e77000000000000000000000000b512e3cf",
        "target_id_mbed_htm": "0240022648cb1e77000000000000000000000000b512e3cf",
        "target_id_usb_id": "0240022648cb1e77000000000000000000000000b512e3cf"
    }
}
```

Let's say we want change ```serial_port```'s value to other COM port. For example we are using other serial port (e.g. while debugging) on our device as standard output.
To do so we would have to create a new file called ```mbedls.json``` in directory where want to use this modification. File content could look like this: a JSON file where keys are ```target_id```'s and values are dictionaries with new values:

```
$ cat mbedls.json
{
    "0240022648cb1e77000000000000000000000000b512e3cf" : {
        "serial_port" : "MyComPort01"
    }
}
```

Now, when we issue ```mbedls``` command in this directory our auto-detection data will be replaced:
```
$ mbedls
+--------------+---------------------+------------+------------+-------------------------------------------------+
|platform_name |platform_name_unique |mount_point |serial_port |target_id                                        |
+--------------+---------------------+------------+------------+-------------------------------------------------+
|K64F          |K64F[0]              |F:          |MyComPort01 |0240022648cb1e77000000000000000000000000b512e3cf |
+--------------+---------------------+------------+------------+-------------------------------------------------+
```

# Mocking new or existing target to custom platform name
Command line switch ```--mock``` provide simple manufacturers ID masking with new platform name.
Users should be able to add temporarily new ```MID``` -> ```platform_name``` mapping when e.g. prototyping.

Mock configuration will be stored in `$HOME/.mbed-ls/` directory, in local file ```.mbedls-mock```.

**Note***: ```MID``` stands for "manufacturers ID". `MID` is first four (4) characters of ```target_id``` string. Example: If ```target_id``` is ```02400221A0811E505D5FE3E8```, corresponding manufacturers ID is ```0240```.

## Mock command line examples
* Mock command line parameter: `--mock` or (switch `-m`)
* Add new / mask existing mapping ```MID``` -> ```platform_name``` and assign `MID`:
    * ```$ mbedls --mock MID:PLATFORM_NAME``` or
    * ```$ mbedls --mock MID1:PLATFORM_NAME1,MID2:PLATFORM_NAME2```
    * Example: `$ mbedls --mock 0818:NUCLEO_F767ZI`
* Remove masking with '!' prefix: `$ mbedls --mock !MID`
* Remove all maskings using !* notation: `$ mbedls --mock !*`
* Combine above using comma (`,`) separator: `$ mbedls --mock MID1:PLATFORM_NAME1,!MID2`

## Mocking example with Freescale K64F platform
Initial setup with 1 x Freescale ```K64F``` board:
```
$ mbedls
+--------------+---------------------+------------+------------+-------------------------+
|platform_name |platform_name_unique |mount_point |serial_port |target_id                |
+--------------+---------------------+------------+------------+-------------------------+
|K64F          |K64F[0]              |F:          |COM146      |02400221A0811E505D5FE3E8 |
+--------------+---------------------+------------+------------+-------------------------+
```

* We can mask current mapping ```0240``` -> ```K64F``` to something else. For example we can replace ```K64F``` name with maybe more suitable for us in current setup ```FRDM-K64F```:
```
$ mbedls --mock 0240:FRDM_K64F
```
Current mocking mapping is stored in local file ```.mbedls-mock```:
```
$ cat .mbedls-mock
{
    "1234": "NEW_PLATFORM_1",
    "0240": "FRDM_K64F"
}
```
We can observe changes immediately. Please note this change only works in the same directory because we save ```.mbedls-mock``` file locally:
```
$ mbedls
+--------------+---------------------+------------+------------+-------------------------+
|platform_name |platform_name_unique |mount_point |serial_port |target_id                |
+--------------+---------------------+------------+------------+-------------------------+
|FRDM_K64F     |FRDM_K64F[0]         |F:          |COM146      |02400221A0811E505D5FE3E8 |
+--------------+---------------------+------------+------------+-------------------------+
```

* We can remove mapping ```1234``` -> Anythying using ```!``` wild-card.
Note: We are using flag ```-json``` to get JSON format output of the ```--mock``` operation.
```
$ mbedls --mock !1234 --json
{
    "0240": "FRDM_K64F"
}
```

* We can add multiple mappings at the same time:
```
$ mbedls --mock 0000:DUMMY,1111:DUMMY_2 --json
{
    "1111": "DUMMY_2",
    "0240": "FRDM_K64F",
    "0000": "DUMMY"
}
```

* We can remove (```!```) all mappings using ```*``` wildcard:
```
$ mbedls --mock !*
```

We can verify our mapping is reset:
```
$ cat $HOME/.mbed-ls/.mbedls-mock
{}
```

# mbed-ls unit testing
* ```mbed-ls``` package contains basic unit tests.
* Tests are stored under ```\mbed-ls\test ``` directory.
* Tests cover basic function calls, object construction and check if minimal requirements for OS porting are fulfilled.
* Standard Python’s ```unittest``` library was used so it is easy to contribute to test effort.
To invoke test procedure from command line please change directory to current mbed-ls repo directory and call setup.py with 'test' option.
```
$ cd mbed-ls
$ python setup.py test
```
```
running test
running egg_info
writing requirements to mbed_ls.egg-info\requires.txt
writing mbed_ls.egg-info\PKG-INFO
writing top-level names to mbed_ls.egg-info\top_level.txt
writing dependency_links to mbed_ls.egg-info\dependency_links.txt
writing entry points to mbed_ls.egg-info\entry_points.txt
reading manifest file 'mbed_ls.egg-info\SOURCES.txt'
writing manifest file 'mbed_ls.egg-info\SOURCES.txt'
running build_ext
test_example (test.basic.BasicTestCase) ... ok
test_detect_os_support_ext (test.detect_os.DetectOSTestCase) ... ok
test_porting_create (test.detect_os.DetectOSTestCase) ... ok
test_porting_mbed_lstools_os_info (test.detect_os.DetectOSTestCase) ... ok
test_porting_mbed_os_support (test.detect_os.DetectOSTestCase) ... ok
.
.
.
----------------------------------------------------------------------
Ran 18 tests in 0.302s

OK
```

## Code coverage

We can measure code coverage for unit tests deployed together with ```mbed-ls```. To do so we can use popular Python ```coverage``` tools.
First install ```coverage``` tool on your system:
```
$ pip install coverage --upgrade
```

Next go to ```mbed-ls``` local directory and execute coverage for unit tests:
```
$ cd mbed-ls
$ coverage run setup.py test
```

Above command will execute test cases and will grab code coverage numbers. Now we are ready to print code coverage for all tests we've run:

```
$ coverage report
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
mbed_lstools\__init__.py                    2      0   100%
mbed_lstools\lstools_base.py              246    169    31%
mbed_lstools\lstools_darwin.py             88     77    13%
mbed_lstools\lstools_linux_generic.py     148     51    66%
mbed_lstools\lstools_ubuntu.py              5      0   100%
mbed_lstools\lstools_win7.py              112     60    46%
mbed_lstools\main.py                       90     63    30%
-----------------------------------------------------------
TOTAL                                     691    420    39%
```

# Configure mbed-enabled device to work with your host

## Windows serial port configuration

The mbed serial port works by default on Mac and Linux, but Windows needs a driver. Check [here](https://developer.mbed.org/handbook/Windows-serial-configuration) for more details.

## Mounting with sync
While working under Ubuntu/Linux/OSX OSs you will have to mount your mbed-enabled device. You can follow instructions how to do it [here](https://developer.mbed.org/handbook/Mounting-with-sync).

### Ubuntu
We recommend you use ```usbmount``` package to auto-mount mbed devices plugged to your host system:

* Install ```usbmount```:

```
$ sudo apt-get install usbmount
```

* Make copy of ```/etc/usbmount/usbmount.conf```:

```
$ sudo cp /etc/usbmount/usbmount.conf /etc/usbmount/usbmount.conf.bak
```

* Modify ```/etc/usbmount/usbmount.conf``` file as follows:

```
ENABLED=1

MOUNTPOINTS="/media/usb0 /media/usb1 /media/usb2 /media/usb3
             /media/usb4 /media/usb5 /media/usb6 /media/usb7
             /media/usb8 /media/usb9 /media/usb10 /media/usb11
             /media/usb12 /media/usb13 /media/usb14 /media/usb15
             /media/usb16 /media/usb17 /media/usb18 /media/usb19"

FILESYSTEMS="vfat ext2 ext3 ext4 hfsplus"

MOUNTOPTIONS="sync,noexec,nodev,noatime,nodiratime"

FS_MOUNTOPTIONS="-fstype=vfat,gid=USERGROUP,uid=USERNAME,dmask=000,fmask=000"

VERBOSE=no
```

*Note*: In line:
```
FS_MOUNTOPTIONS="-fstype=vfat,gid=USERGROUP,uid=USERNAME,dmask=000,fmask=000"
```
change ```USERGROUP``` and ```USERNAME``` to your user and group names.

You can check user "USERNAME" group by typing:
```
$ groups USERNAME
```

This ```usbmount``` configuration will auto-mount your mbed devices without need to type ```mount``` commands each time you plug your mbeds!

## Raspberry Pi - Raspbian Jessie Lite
For Raspberry Pi you can use [LDM](https://github.com/LemonBoy/ldm): A lightweight device mounter. This should improve stability of your mounts when using mbed-ls on Raspberry Pi. Currently we are using it with _Raspbian Jessie Lite_.

How to install and use LDM on your Raspberry Pi in three easy steps:

### Prerequisites
LDM requires additional packages installed (libudev, mount and glib-2.0). You can use below command to check if all requirements are fulfilled:
```
$ pkg-config --cflags libudev mount glib-2.0
```

You may need to install additional packages:

```
$ sudo apt-get install libudev1
$ sudo apt-get install libudev-dev
$ sudo apt-get install libmount-dev
$ sudo apt-get install libglib2.0-dev
```

Note: You may want to issue ```$ sudo apt-get update``` to make sure that you have access to latest packages via apt-get.

### Install LDM
```
$ git clone git@github.com:LemonBoy/ldm.git
$ cd ldm
$ sudo make install
```

Add LDM configuration file and configuration itself. Remember to change the ```your_own_user_name``` to valid username.
```
$ sudo touch /etc/ldm.conf
$ echo 'MOUNT_OWNER=your_own_user_name' >> /etc/ldm.conf
$ echo 'BASE_MOUNTPOINT=/mnt' >> /etc/ldm.conf
```

### Enable LDM
```
$ systemctl status ldm
$ sudo systemctl enable ldm
```

Now you probably have to safely reboot to make sure changes will take place ```$sudo shutdown -r now (or sudo reboot)``` and enjoy more stable ```mbed-ls``` queries with your Raspberry Pi (Raspbian Jessie Lite).

### Making sure LDM is active (running)

```
$ systemctl status ldm
```
```
ldm.service - lightweight device mounter
  Loaded: loaded (/usr/lib/systemd/system/ldm.service; enabled)
  Active: active (running) since Fri 2016-04-29 12:54:23 UTC; 48min ago
Main PID: 389 (ldm)
  CGroup: /system.slice/ldm.service
          └─389 /usr/bin/ldm -u jenkins -p /mnt
```

# Known issues
* Users reported issues while using ```mbed-ls``` on VM (Virtual Machines).
* **[FIXED in v1.2.0]** [mbedls fails to list devices on OS X El Capitan](https://github.com/ARMmbed/mbed-ls/issues/38).
* **[FIXED in v0.2.5]**```mbed-ls``` doesn't list not mounted devices (Ubuntu/Linux).
