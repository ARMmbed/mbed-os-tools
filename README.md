[![Build status](https://circleci.com/gh/ARMmbed/mbed-ls/tree/master.svg?style=svg)](https://circleci.com/gh/ARMmbed/mbed-ls/tree/master)
[![Coverage Status](https://coveralls.io/repos/github/ARMmbed/mbed-ls/badge.svg?branch=master)](https://coveralls.io/github/ARMmbed/mbed-ls?branch=master)
[![PyPI version](https://badge.fury.io/py/mbed-ls.svg)](https://badge.fury.io/py/mbed-ls)

# mbed-ls

`mbed-ls` is a Python (2 and 3) module that detects and lists Mbed Enabled devices connected to the host computer. It is delivered as a redistributable Python module (package) and command-line tool. It works on all major operating systems (Windows, Linux and Mac OS X).

It provides the following information for all connected boards in a simple console (terminal) output:

- Mbed OS platform name.
- Mount point (MSD or disk).
- Serial port.

# Installation

## Installation from PyPI (Python Package Index)

To install `mbed-ls` from [PyPI](https://pypi.python.org/pypi/mbed-ls), run the following command:

```bash
pip install mbed-ls --upgrade
```

## Installation from Python sources

**Prerequisites:** You need to have [Python 2.7.x](https://www.python.org/download/releases/2.7/) or [Python 3.6.x](https://www.python.org/downloads/release/python-362/) installed on your system.

**Note:** If your OS is Windows, please follow the installation instructions [for the serial port driver](https://os.mbed.com/docs/latest/tutorials/windows-serial-driver.html).

To install the `mbed-ls` module, first clone the `mbed-ls` repository. The following example uses the GitHub command-line tools, but you can do this directly from the website:

```bash
git clone https://github.com/ARMmbed/mbed-ls.git
cd mbed-ls
python setup.py install
```

# Use

## Command-line

The command-line tool is available with the command `mbedls`:

```bash
$ mbedls
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| platform_name | platform_name_unique | mount_point | serial_port | target_id                                        | daplink_version |
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| K64F          | K64F[0]              | D:          | COM18       | 0240000032044e4500257009997b00386781000097969900 | 0244            |
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
```

### Result formats

The command-line is able to list the results in a number of formats.

#### Simple (no table formatting)

```
$ mbedls --simple
 K64F  K64F[0]  D:  COM18  0240000032044e4500257009997b00386781000097969900  0244
```

#### JSON

```bash
$ mbedls --json
[
    {
        "daplink_auto_reset": "0",
        "daplink_automation_allowed": "1",
        "daplink_bootloader_crc": "0xa65218eb",
        "daplink_bootloader_version": "0242",
        "daplink_daplink_mode": "Interface",
        "daplink_git_sha": "67f8727a030bcc585e982d899fb6382db56d673b",
        "daplink_hic_id": "97969900",
        "daplink_interface_crc": "0xe4422294",
        "daplink_interface_version": "0244",
        "daplink_local_mods": "0",
        "daplink_overflow_detection": "1",
        "daplink_remount_count": "0",
        "daplink_unique_id": "0240000032044e4500257009997b00386781000097969900",
        "daplink_usb_interfaces": "MSD, CDC, HID",
        "daplink_version": "0244",
        "mount_point": "D:",
        "platform_name": "K64F",
        "platform_name_unique": "K64F[0]",
        "serial_port": "COM18",
        "target_id": "0240000032044e4500257009997b00386781000097969900",
        "target_id_mbed_htm": "0240000032044e4500257009997b00386781000097969900",
        "target_id_usb_id": "0240000032044e4500257009997b00386781000097969900"
    }
]
```

### Mocking (renaming) platforms

When developing new a platform, it is possible to override the default name `mbed-ls` assigns. This is done with the `--mock` parameter:

```
$ mbedls --mock 0240:MY_NEW_PLATFORM
$ mbedls
+-----------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| platform_name   | platform_name_unique | mount_point | serial_port | target_id                                        | daplink_version |
+-----------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| MY_NEW_PLATFORM | MY_NEW_PLATFORM[0]   | D:          | COM18       | 0240000032044e4500257009997b00386781000097969900 | 0244            |
+-----------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
```

Where `0204` is the leading 4 characters of the platform's `target_id`.

To remove a mocked platform, use the `--mock` parameter again. For the value, use `-<4 leading characters of the target_id>`:

```
$ mbedls --mock -0240
$ mbedls
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| platform_name | platform_name_unique | mount_point | serial_port | target_id                                        | daplink_version |
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| K64F          | K64F[0]              | D:          | COM18       | 0240000032044e4500257009997b00386781000097969900 | 0244            |
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
```

You can also remove all mocked platforms by supplying `*` as the `target_id`:

```
$ mbedls --mock="-*"
```

**NOTE:** Due to a quirk in the parameter formatting, the command-line can interpret `-*` as another parameter instead of a value. It is necessary to use the complete `--mock="-*"` syntax, so the command-line interprets each part of the command correctly.

### Retargeting platforms

It is possible to change the returned results for certain platforms depending on the current directory. This is especially useful when developing new platforms.

The command-line tool and Python API check the current directory for a file named `mbedls.json`. If it is present, it overrides the returned values. The format of the `mbedls.json` file is:

```json
{
    "<target_id>": {
        "<key>": "<value>"
    }
}
```

For example, to change the `serial_port` of the K64F with a `target_id` of `0240000032044e4500257009997b00386781000097969900`, the `mbedls.json` file contains the following:

```json
{
    "0240000032044e4500257009997b00386781000097969900": {
        "serial_port": "COM99"
    }
}
```

This results in the following output from the command-line tool:

```bash
$ mbedls
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| platform_name | platform_name_unique | mount_point | serial_port | target_id                                        | daplink_version |
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| K64F          | K64F[0]              | D:          | COM99       | 0240000032044e4500257009997b00386781000097969900 | 0244            |
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
```

Note how the `serial_port` value changed from `COM18` to `COM99`. Deleting the `mbedls.json` or using the `--skip-retarget` parameter removes these changes.

## Python API

---

### `mbeds.mbed_lstools.create(...)`

The Python API is available through the `mbed_lstools` module.

```python
>>> import mbed_lstools
>>> mbeds = mbed_lstools.create()
>>> mbeds
<mbed_lstools.lstools_win7.MbedLsToolsWin7 instance at 0x02F542B0>
```

This returns an instance that provides access to the rest of the API.

#### Arguments

##### `skip_retarget`

**Default:** `False`

If set to `True`, this skips the retargetting step, and the results are unmodified.

##### `list_unmounted`

**Default:** `False`

If set to `True`, this includes unmounted platforms in the results.

---

### `mbeds.list_mbeds(...)`

```python
>>> import mbed_lstools
>>> mbeds = mbed_lstools.create()
>>> mbeds.list_mbeds(fs_interaction=FSInteraction.BeforeFilter,
                                    filter_function=None,
                                    unique_names=False,
                                    read_details_txt=False)
[{'target_id_mbed_htm': u'0240000032044e4500257009997b00386781000097969900', 'mount_point': 'D:', 'target_id': u'0240000032044e4500257009997b00386781000097969900', 'serial_port': u'COM18', 'target_id_usb_id': u'0240000032044e4500257009997b00386781000097969900', 'platform_name': u'K64F'}]
```

#### Arguments

##### `fs_interaction`

**Default:** `FSInteraction.BeforeFilter`

This argument controls the accuracy and speed of this function. There are three choices (in ascending order of accuracy and decreasing order of speed):

- `FSInteraction.NEVER` - This is the fastest option but also potentially the least accurate. It never touches the file system of the devices and uses only the information available through the OS. This is appropriate for use in a highly controlled environment (such as an automated Continuous Integration setup). **This has the potential to provide incorrect names and data. It may also lead to devices not being detected at all.**
- `FSInterfaction.AfterFilter` - This accesses the file system but only after you apply the `filter_function`. This can lead to speed increases but at the risk of filtering on inaccurate information.
- `FSInteraction.BeforeFilter` - This accesses the file system before doing any filtering. It is the most accurate option and is recommended for most uses. This is the default behavior of the command-line tool and the API.

##### `filter_function`

**Default:** `None`

This function allows you to filter results based on platform data. This can hasten the execution of the `list_mbeds` function.

As a normal function definition:

```python
def filter_func(mbed):
    return m['platform_name'] == 'K64F'

mbeds.list_mbeds(filter_function=filter_func)
```

As a lambda function:

```python
platforms = mbeds.list_mbeds(filter_function=lambda m: m['platform_name'] == 'K64F')
```

##### `unique_names`

**Default:** `False`.

This controls whether a unique name is assigned to each platform. The unique name takes the form of `K64F[0]`, where the number between the brackets is an incrementing value. This name is accessible through the dictionary member `platform_unique_name` in the returned platform data. It defaults to `False`.

##### `read_details_txt`

**Default:** `False`

This controls whether more data is pulled from the file system on each device. It can provide useful management data but also takes more time to execute.

---

### `mock_manufacture_id(...)`

```python
>>> import mbed_lstools
>>> mbeds = mbed_lstools.create()
>>> mbeds.mock_manufacture_id('0240', 'CUSTOM_PLATFORM', oper='+')
>>> mbeds.list_mbeds()
[{'target_id': u'0240000032044e4500257009997b00386781000097969900', ... 'platform_name': u'CUSTOM_PLATFORM'}]
>>> mbeds.mock_manufacture_id('0240', '', oper='-')
>>> mbeds.list_mbeds()
[{'target_id': u'0240000032044e4500257009997b00386781000097969900', ... 'platform_name': u'K64F'}]
```

#### Arguments

##### `mid`

**Required**

The first four characters of the TargetID that you want to mock.

##### `platform_name`

**Required**

The name of the platform that is returned for any platform that has a `target_id` that matches the first four characters specified in `mid`.

##### `oper`

**Default:** `'+'`

If set to `'+'`, the mocked platform is enabled. If `'-'`, the mocked platform is disabled.

---

# Testing

All tests are contained within the `/test` directory. You can run the tests with the following command:

```
$ python setup.py test
```

## Code coverage

The `coverage` Python package measures code coverage. You can install it with following command:

```
$ pip install coverage --upgrade
```

To run the tests while measuring code coverage, use the following command:

```
$ coverage run setup.py test
```

You can then generate a report:

```
$ coverage report
Name                                Stmts   Miss  Cover
-------------------------------------------------------
mbed_lstools\__init__.py                2      0   100%
mbed_lstools\darwin.py                 85      7    92%
mbed_lstools\linux.py                  45      3    93%
mbed_lstools\lstools_base.py          299    124    59%
mbed_lstools\main.py                  134     44    67%
mbed_lstools\platform_database.py     114      4    96%
mbed_lstools\windows.py                98     21    79%
-------------------------------------------------------
TOTAL                                 777    203    74%
```

# OS-specific behavior

## Windows

The Mbed serial port works by default on Mac and Linux, but Windows needs a driver. Check [here](https://os.mbed.com/docs/latest/tutorials/windows-serial-driver.html) for more details.

## Linux

`mbed-ls` requires you to mount a platform before it shows up in the results. Many Linux systems do not automatically mount USB devices. We recommend you use an automounter to manage this for you.

There are many automounters available, and it is ultimately up to you to determine which is the best one for your use case. However, the `usbmount` package on Ubuntu makes it easy to start. If you need more control over your automounter, you can build and run an open source project called [ldm](https://github.com/LemonBoy/ldm).

# Mbed Enabled technical requirements overview

This tool relies on board interfaces conforming to certain standards, so it can detect platforms properly. The [Mbed Enabled](https://www.mbed.com/en/about-mbed/mbed-enabled/) program sets these standards. Please see the [Technical Requirements](https://www.mbed.com/en/about-mbed/mbed-enabled/mbed-enabled-program-requirements/) for more information.

## Device unique identifier

Each device must have a unique identifier. This identifier has two parts: a **TargetID** and a **platform unique string**.

The **TargetID** contains four ASCII characters containing only hexadecimal values (A-F and 0-9). This TargetID is the same for all platforms of the same type. For example, all `K64F` platforms have a TargetID of `0240`. `mbedls` uses this to identify the platform.

The **platform unique string** can be any length of characters (a-z, A-Z and 0-9) that you can use to uniquely identify platforms of the same type on the same machine. For example, two FRDM-K64F platforms attached to the same machine could have the following attributes:

```
$ mbedls
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| platform_name | platform_name_unique | mount_point | serial_port | target_id                                        | daplink_version |
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
| K64F          | K64F[0]              | D:          | COM18       | 0240000032044e4500257009997b00386781000097969900 | 0244            |
| K64F          | K64F[1]              | E:          | COM19       | 0240000032044e4500257009997b00386781000097840023 | 0244            |
+---------------+----------------------+-------------+-------------+--------------------------------------------------+-----------------+
```

Note how both platforms share the same TargetID (`0240`) but have a unique ending string.
