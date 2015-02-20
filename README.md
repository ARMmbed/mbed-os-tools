## Description
mbed-lstools is module used to detect and list mbed-enabled devices connected to host computer.
Currently lmtools support listed below OSs:
* Windows 7.
* Ubuntu.
* Mac OS X (Darwin)

mbed-ls is Python module used to detect and list mbed-enabled devices connected to host computer. package will support Windows 7, Ubuntu and MacOS. It will be delivered as redistributable Python module (package) and command line tool.
Currently mbed-ls module is under development but already decoupled mbed-ls functionality is delivered to mbed SDK's test suite.

You will be able for example to use this tool from command line! (See below)
### mbedls command line tool
After installing mbed-ls package on your system will be deployed importable ```mbed_lstools``` Python package and ```mbedls``` command line tool:
```
$ mbedls
+---------------------+-------------------+-------------------+--------------------------------+
|platform_name        |mount_point        |serial_port        |target_id                       |
+---------------------+-------------------+-------------------+--------------------------------+
|KL25Z                |I:                 |COM89              |02000203240881BBD9F47C43        |
|NUCLEO_F302R8        |E:                 |COM34              |07050200623B61125D5EF72A        |
+---------------------+-------------------+-------------------+--------------------------------+
```

```mbedls``` command will allow you to list all connected mbed-enabled devices and correctly associate mbed-enabled board mount point (disk) and serial port. Additionally TargetID information will be provided for your reference. Because we are all automation fanatics ```mbedls``` command will also output mbed-enabled auto-detection data in JSON format.
If you want to use ```mbedls``` in your toolchain, continuous integration or automation script and do not necessarily want to use Python module ```mbed_lstools``` this solution is for you.

### Exporting mbedls output to JSON
You can export mbedls output to JSON format, just use ```---json``` switch and dump your file on screen or redirect to file. It should help you further automate your processes! 
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

### Rationale
When connecting more than one mbed-enabled device to host computer it takes time to check platform's binds:
* Mounted disk.
* Virtual serial port.
* Mbed's TargetID and generic platform name.

# Installation from Python sources 
Prerequisites: you need to have Python 2.7.x installed on your system.

To install mbed-ls module clone mbed-ls repository:
```
$ git clone <link-to-mbed-ls-repo>
```
and change directory to mbed-ls repository directory:
```
$ cd mbed-ls
```
Now you are ready to install mbed-ls. 
```
$ python setup.py install
```
Above command should install ```mbed-ls``` Python package (import ```mbed_lstools```) and mbedls command:

To test if your installation succeeded try ```mbedls``` command:
```
$ mbedls
```
Or use Python interpreter and import ```mbed_lstools```  to check if module is correctly installed:
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
[]
>>> print mbeds
```
Note: On Linux if you have problem with permissions please try to use ```sudo```:
```
$ sudo python setup.py install
```


# Installation from PyPI (Python Package Index)
In the near furure mbed-ls module can be redistributed via PyPI. We recommend you use ```pip``` application. It is available here: https://pip.pypa.io/en/latest/installing.html#install-pip

Note: Python 2.7.9 and later (on the python2 series), and Python 3.4 and later include pip by default, so you may have pip already.

# Porting instructions
YOu can help us improve mbned-ls tools by for example commiting new OS port. Currently in 'Description' section of this readme we are presenting you with list of supported OSs. If your OS is not on the list you can always port it!

For further study please check how Mac OS X (Darwin) was ported in this pull request: https://github.com/ARMmbed/mbed-ls/pull/1.

## mbed-ls auto-detection approach for Ubuntu
Let's connect few mbed boards to our Ubuntu host. Devices should mount MSC and CDC (virtual disk and serial port).
We can see mounting result for example in usb-id directories in Ubuntu file system under ```/dev/```.

We've connected in this example to USB ports of our Ubuntu machine:
* 2 x STMicro's Nucleo mbed boards.
* 2 x NXP mbed boards.
* 1 x Feescale Freedom board.

Serial ports (CDC) mounted via USB interface mbed boards provide:
```
$ ll /dev/serial/by-id
total 0
drwxr-xr-x root 140 Feb 19 12:38 ./
drwxr-xr-x root  80 Feb 19 12:35 ../
lrwxrwxrwx root  13 Feb 19 12:38 usb-MBED_MBED_CMSIS-DAP_02000203240881BBD9F47C43-if01 -> ../../ttyACM0
lrwxrwxrwx root  13 Feb 19 12:35 usb-MBED_MBED_CMSIS-DAP_A000000001-if01 -> ../../ttyACM4
lrwxrwxrwx root  13 Feb 19 12:35 usb-mbed_Microcontroller_101000000000000000000002F7F18695-if01 -> ../../ttyACM3
lrwxrwxrwx root  13 Feb 19 12:35 usb-STMicroelectronics_STM32_STLink_066EFF525257775087141721-if02 -> ../../ttyACM2
lrwxrwxrwx root  13 Feb 19 12:35 usb-STMicroelectronics_STM32_STLink_066EFF534951775087215736-if02 -> ../../ttyACM1
```

Disks (MSC) mounted via USB interface mbed boards provide:
```
$ ll /dev/disk/by-id
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
Note: We can see that on our host machine with Ubuntu system we have many 'disk type' devices visible under ```/dev/disk```.
Note some of them are mbed boards and can be distingushed by unique ```USB-ID```.

```mbed-ls``` tools are pairing only serial ports and mount points (not CMSIS-DAP yet) together.
On Ubuntu Linux we are checking usb-ids of all devices which may be mbed boards. We know mbed boards follow few ```usb-id``` conventions which can be used filter out mbed devices' ```usb-ids```.

In our case we can see pairs of ```usb-ids``` in both ```/dev/serial/usb-id``` and ```/dev/disk/usb-id``` with embedded ``` TargetID```.  ```TargetID``` can be filtered out for example using this sudo-regexpr: ```(“MBED”|”mbed”|”STMicro”)_([a-zA-z_-]+)_([a-fA_F0-0]){4,}```

For example we can match board 066EFF525257775087141721 by connecting few dots:
* ```usb-MBED_microcontroller_066EFF525257775087141721-0:0 -> ../../sdd``` and
* ```usb-STMicroelectronics_STM32_STLink_066EFF525257775087141721-if02 -> ../../ttyACM2```
Based on marked with red color TargetID hash.

From there we know that target platform has these properties:
* Unique target platform identifier is ```066E```.
* Serial port is ```ttyACM2```.
* Mount point is ```sdd```.
Your ```mbed-ls``` implementation must resolve those three and create “tuple” with those values (for each connected device).
If you have this tuple(s) other mbed-ls will carry on with platform number to human readable name conversion etc.

Note that for some boards ```TargetID``` format is proprietary (See STMicro boards) and ```usb-id``` does not have valid TargetID where four first letters are target platform unique ID.
In that case ```mbed-ls``` tools should inspect ```mbed.htm``` file on mbed mounted disk. ```mbed-ls``` tools will disect ```mbed.htm``` get proper TagretID from URL in ```meta``` part of the HTML header.

In below example URL ```http://mbed.org/device/?code=07050200623B61125D5EF72A``` for STMicto Nucleo F302R8 board contains valid TargetID ```07050200623B61125D5EF72A``` which can be used to detect ```platform_name``` by ```mbed-ls``` tools.
Note: ```mbed-ls``` tools will replace ```usb-id``` invalid TargetID with targetID from ```mbed.htm```.

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

Example of ```mbedls``` listing for connected devices.
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
