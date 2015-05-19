## Description

<<<<<<< HEAD
mbed-lstools is a Python module that detects and lists mbed-enabled devices connected to the host computer. It will be delivered as a redistributable Python module (package) and command line tool.

Currently supported operating system:

=======
mbed-lstools is a module used to detect and list mbed-enabled devices connected to the host computer.

Currently lmtools support the following OSs:
>>>>>>> master
* Windows 7.
* Ubuntu.
* Mac OS X (Darwin).

<<<<<<< HEAD
The stand-alone mbed-lstools Python package is still under development, but it's already delivered as part of the mbed SDK's test suite and a command line tool (see below).

## Rationale

When connecting more than one mbed-enabled device to the host computer, it takes time to manually check the platforms' binds:

* Mount point (disk).
* Virtual serial port.
* mbed's TargetID and generic platform name.

mbedls provides these points of information for all connected boards at once in a simple console (terminal) output.

**Tip:** Because we are all automation fanatics, the ```mbedls``` command will also output mbed-enabled auto-detection data in JSON format (see below).

## Installation from Python sources 

**Prerequisites:** you need to have [Python 2.7.x](https://www.python.org/download/releases/2.7/) installed on your system.

**Note:** if your OS is Windows, please follow the installation instructions [for the serial port driver](https://developer.mbed.org/handbook/Windows-serial-configuration).

To install the mbed-ls module:

Clone the mbed-ls repository. The following example uses the GitHub command line tools, but you can do this directly from the website:

```
$ git clone <link-to-mbed-ls-repo>

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
```
>>> import mbed_lstools
>>> mbeds = mbed_lstools.create()
>>> mbeds
<mbed_lstools.lstools_win7.MbedLsToolsWin7 instance at 0x02F542B0>
>>> mbeds.list_mbeds()
[{'platform_name': 'K64F', 'mount_point': 'E:', 'target_id': '02400203D94B0E7724B7F3CF', 'serial_port': u'COM61'}]
>>> print mbeds
```

## Installation from PyPI (Python Package Index)

In the near future the mbed-ls module will be redistributed via PyPI. We recommend you use the [```pip``` application](here: https://pip.pypa.io/en/latest/installing.html#install-pip).

**Note:** Python 2.7.9 and later (on the Python 2 series), and Python 3.4 and later include pip by default, so you may have pip already.

## mbedls command line tool

After installation of the mbed-ls package, you can use the mbedls command. It allows you to list all connected mbed-enabled devices and gives you the correct association between your board mount point (disk) and the serial port. TargetID information is also provided for your information.

=======
mbed-ls is a Python module used to detect and list mbed-enabled devices connected to the host computer. The package will support Windows 7, Ubuntu and MacOS. It will be delivered as a redistributable Python module (package) and command line tool.

Currently the mbed-ls module is under development but its already decoupled mbed-ls functionality is delivered to mbed SDK's test suite.

You will be able, for example, to use this tool from the command line! (See below)

### mbedls command line tool

After installing the mbed-ls package on your system, the importable ```mbed_lstools``` Python package and ```mbedls``` command line tool will be deployed:

>>>>>>> master
```
$ mbedls
+---------------------+-------------------+-------------------+--------------------------------+
|platform_name        |mount_point        |serial_port        |target_id                       |
+---------------------+-------------------+-------------------+--------------------------------+
|KL25Z                |I:                 |COM89              |02000203240881BBD9F47C43        |
|NUCLEO_F302R8        |E:                 |COM34              |07050200623B61125D5EF72A        |
+---------------------+-------------------+-------------------+--------------------------------+
```

<<<<<<< HEAD
If you want to use ```mbedls``` in your toolchain, continuous integration or automation script and do not necessarily want to use the Python module ```mbed_lstools``` - this solution is for you.

### Exporting mbedls output to JSON

You can export mbedls outputs to JSON format: just use the ```---json``` switch and dump your file on the screen or redirect to a file. It should help you further automate your processes.
=======
The command```mbedls``` will allow you to list all connected mbed-enabled devices and correctly associate the mbed-enabled board mount point (disk) and serial port. Additionally, TargetID information will be provided for your reference. Because we are all automation fanatics the ```mbedls``` command will also output the mbed-enabled auto-detection data in JSON format.

If you want to use ```mbedls``` in your toolchain, continuous integration or automation script and do not necessarily want to use Python module ```mbed_lstools``` - this solution is for you.

### Exporting mbedls output to JSON

You can export the mbedls output to JSON format: just use the ```---json``` switch and dump your file on the screen or redirect to the file. It should help you further automate your processes! 
>>>>>>> master

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

<<<<<<< HEAD
## mbed-ls auto-detection approach for Ubuntu
=======
### Rationale

When connecting more than one mbed-enabled device to the host computer it takes time to check the platform's binds:
* Mounted disk.
* Virtual serial port.
* Mbed's TargetID and generic platform name.

# Installation from Python sources 

Prerequisites: you need to have Python 2.7.x installed on your system.

To install the mbed-ls module, clone the mbed-ls repository:
```
$ git clone <link-to-mbed-ls-repo>
```
and change the directory to the mbed-ls repository directory:
```
$ cd mbed-ls
```
Now you are ready to install mbed-ls. 
```
$ python setup.py install
```
The above command should install the ```mbed-ls``` Python package (import ```mbed_lstools```) and mbedls command:

To test if your installation succeeded try the ```mbedls``` command:
```
$ mbedls
```
Or use the Python interpreter and import ```mbed_lstools```  to check if the module is correctly installed:
```
$ python
Python 2.7.8 (default, Jun 30 2014, 16:03:49) [MSC v.1500 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
```
```
>>> import mbed_lstools
>>> mbeds = mbed_lstools.create()
>>> mbeds
<mbed_lstools.lstools_win7.MbedLsToolsWin7 instance at 0x02F542B0>
>>> mbeds.list_mbeds()
[{'platform_name': 'K64F', 'mount_point': 'E:', 'target_id': '02400203D94B0E7724B7F3CF', 'serial_port': u'COM61'}]
>>> print mbeds
```
Note: On Linux if you have a problem with permissions please try to use ```sudo```:
```
$ sudo python setup.py install
```

# Installation from PyPI (Python Package Index)
In the near future the mbed-ls module can be redistributed via PyPI. We recommend you use the ```pip``` application. It is available here: https://pip.pypa.io/en/latest/installing.html#install-pip

Note: Python 2.7.9 and later (on the python2 series), and Python 3.4 and later include pip by default, so you may have pip already.

# Porting instructions
You can help us improve the mbed-ls tools by, for example, committing a new OS port. The '[Description](#description)' section of this readme presents a list of supported OSs. If your OS is not on the list you can always port it!
>>>>>>> master

Let's connect  a few mbed boards to our Ubuntu host. The devices should mount as MSC and CDC (virtual disk and serial port). We'll use regular Linux commands to see the boards, then see how ```mbed-ls``` displays them.

<<<<<<< HEAD
In this example, we've connected to our Ububtu machine's USB ports:

=======
## mbed-ls auto-detection approach for Ubuntu
Let's connect a few mbed boards to our Ubuntu host. The devices should mount MSC and CDC (virtual disk and serial port).
We can see the mounting result, for example, in the usb-id directories in the Ubuntu file system under ```/dev/```.

We've connected in this example to the USB ports of our Ubuntu machine:
>>>>>>> master
* 2 x STMicro's Nucleo mbed boards.
* 2 x NXP mbed boards.
* 1 x Freescale Freedom board.

<<<<<<< HEAD
We can see the mounting result in the usb-id directories in Ubuntu's file system under ```/dev/```. To list mbed boards mounted to serial ports (CDC) via USB, we use the general Linux command:

=======
Serial ports (CDC) mounted via the USB interface mbed boards provide:
>>>>>>> master
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

<<<<<<< HEAD
To list boards mounted to disks (MSC) via USB, we use the general Linux command:
=======
Disks (MSC) mounted via the USB interface mbed boards provide:
>>>>>>> master
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
<<<<<<< HEAD

***Note:*** ```mbed-ls``` tools pair only serial ports and mount points (not CMSIS-DAP - yet).

We can see that on our host machine (running Ubuntu) there are many 'disk type' devices visible under ```/dev/disk```. The mbed boards can be distinguished and filtered by their unique ```USB-ID``` conventions. In our case, we can see pairs of ```usb-ids``` in both ```/dev/serial/usb-id``` and ```/dev/disk/usb-id``` with embedded ``` TargetID```.  ```TargetID``` can be filtered out, for example using this sudo-regexpr: ```(“MBED”|”mbed”|”STMicro”)_([a-zA-z_-]+)_([a-fA_F0-0]){4,}```

For example, we can match the board 066EFF525257775087141721 by connecting a few dots:

* ```usb-MBED_microcontroller_066EFF525257775087141721-0:0 -> ../../sdd```
* ```usb-STMicroelectronics_STM32_STLink_066EFF525257775087141721-if02 -> ../../ttyACM2``` Based on the TargetID hash.
=======
Note: We can see that on our host machine with the Ubuntu system we have many 'disk type' devices visible under ```/dev/disk```.
Note that some of them are mbed boards and can be distinguished by a unique ```USB-ID```.

The```mbed-ls``` tools are pairing only the serial ports and mount points (not CMSIS-DAP yet) together.
On Ubuntu Linux we are checking the usb-ids of all the devices which may be mbed boards. We know that mbed boards follow a few ```usb-id``` conventions which can be used to filter out the mbed devices' ```usb-ids```.
>>>>>>> master

From this we know that the target platform has these properties:

<<<<<<< HEAD
* The unique target platform identifier is ```066E```.
* The serial port is ```ttyACM2```.
* The mount point is ```sdd```.

Your ```mbed-ls``` implementation resolves those three and creates a “tuple” with those values (for each connected device). Using this tuple(s), ```mbed-ls``` will convert the platform number to a human-readable name etc.

Note that for some boards the ```TargetID``` format is proprietary (see STMicro boards) and ```usb-id``` does not have a valid TargetID where the four first letters are the target platform's unique ID. In that case, ```mbed-ls``` tools inspects the ```mbed.htm``` file on the mbed mounted disk to get the proper TargetID from the URL in the ```meta``` part of the HTML header.

In the following example, the URL ```http://mbed.org/device/?code=07050200623B61125D5EF72A``` for the STMicro Nucleo F302R8 board contains the valid TargetID ```07050200623B61125D5EF72A```, which ```mbed-ls``` uses to detect the ```platform_name```. ```mbed-ls``` will then replace the invalid TargetID in ```usb-id``` with the value from ```mbed.htm```.
=======
For example we can match the board 066EFF525257775087141721 by connecting a few dots:
* ```usb-MBED_microcontroller_066EFF525257775087141721-0:0 -> ../../sdd``` and
* ```usb-STMicroelectronics_STM32_STLink_066EFF525257775087141721-if02 -> ../../ttyACM2```
Based on the TargetID hash marked in red.

From there we know that the target platform has these properties:
* The unique target platform identifier is ```066E```.
* The serial port is ```ttyACM2```.
* The mount point is ```sdd```.
Your ```mbed-ls``` implementation must resolve those three and create a “tuple” with those values (for each connected device).
If you have this tuple(s) other mbed-ls will carry on with the platform number to a human readable name conversion etc.

Note that for some boards the ```TargetID``` format is proprietary (See STMicro boards) and ```usb-id``` does not have a valid TargetID where the four first letters are the target platform unique ID.
In that case the ```mbed-ls``` tools should inspect the ```mbed.htm``` file on the mbed mounted disk. ```mbed-ls``` tools will dissect  ```mbed.htm``` to get the proper TargetID from the URL in the ```meta``` part of the HTML header.

In the example below the URL ```http://mbed.org/device/?code=07050200623B61125D5EF72A``` for the STMicro Nucleo F302R8 board contains the valid TargetID ```07050200623B61125D5EF72A``` which can be used to detect the ```platform_name``` with the ```mbed-ls``` tools.
Note: ```mbed-ls``` tools will replace the ```usb-id``` invalid TargetID with a TargetID from ```mbed.htm```.
>>>>>>> master

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

## Porting instructions

You can help us improve the mbed-ls tools by - for example - committing a new OS port. You can see the list of currently supported OSs in the [Description](#description) section; if your OS isn't there, you can port it.

For further study please check how Mac OS X (Darwin) was ported in [this pull request](https://github.com/ARMmbed/mbed-ls/pull/1).
