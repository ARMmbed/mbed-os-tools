#!/usr/bin/env python

"""
mbed SDK
Copyright (c) 2011-2015 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
import json
import platform
from collections import defaultdict

# Make sure that any global generic setup is run
from . import lstools_base

import logging
logger = logging.getLogger("mbedls.main")
logger.addHandler(logging.NullHandler())
del logging


def create(**kwargs):
    """! Factory used to create host OS specific mbed-lstools object

    :param kwargs: keyword arguments to pass along to the constructors
    @return Returns MbedLsTools object or None if host OS is not supported

    """
    result = None
    mbed_os = mbed_os_support()
    if mbed_os is not None:
        if mbed_os == 'Windows7':
            from .windows import MbedLsToolsWin7
            result = MbedLsToolsWin7(**kwargs)
        elif mbed_os == 'LinuxGeneric':
            from .linux import MbedLsToolsLinuxGeneric
            result = MbedLsToolsLinuxGeneric(**kwargs)
        elif mbed_os == 'Darwin':
            from .darwin import MbedLsToolsDarwin
            result = MbedLsToolsDarwin(**kwargs)
    return result


def mbed_os_support():
    """! Function used to determine if host OS is supported by mbed-lstools

    @return Returns None if host OS is not supported else return OS short name

    @details This function should be ported for new OS support
    """
    result = None
    os_info = mbed_lstools_os_info()
    if (os_info[0] == 'nt' and os_info[1] == 'Windows'):
        result = 'Windows7'
    elif (os_info[0] == 'posix' and os_info[1] == 'Linux'):
        result = 'LinuxGeneric'
    elif (os_info[0] == 'posix' and os_info[1] == 'Darwin'):
        result = 'Darwin'
    return result


def mbed_lstools_os_info():
    """! Returns information about host OS

    @return Returns tuple with information about OS and host platform
    """
    result = (os.name,
              platform.system(),
              platform.release(),
              platform.version(),
              sys.platform)
    return result

def print_mbeds(mbeds, args, simple):
    devices = mbeds.list_mbeds(unique_names=True, read_details_txt=True)
    if devices:
        from prettytable import PrettyTable, HEADER
        columns = ['platform_name', 'platform_name_unique', 'mount_point',
                    'serial_port', 'target_id', 'daplink_version']
        pt = PrettyTable(columns, junction_char="|", hrules=HEADER)
        pt.align = 'l'
        for d in devices:
            pt.add_row([d.get(col, None) or 'unknown' for col in columns])
        print(pt.get_string(border=not simple, header=not simple,
                            padding_width=1, sortby='platform_name_unique'))

def print_table(mbeds, args):
    return print_mbeds(mbeds, args, False)

def print_simple(mbeds, args):
    return print_mbeds(mbeds, args, True)

def mock_platform(mbeds, args):
    for token in args.mock.split(','):
        if ':' in token:
            oper = '+' # Default
            mid, platform_name = token.split(':')
            if mid and mid[0] in ['+', '-']:
                oper = mid[0]   # Operation (character)
                mid = mid[1:]   # We remove operation character
            mbeds.mock_manufacture_id(mid, platform_name, oper=oper)
        elif token and token[0] in ['-', '!']:
            # Operations where do not specify data after colon: --mock=-1234,-7678
            oper = token[0]
            mid = token[1:]
            mbeds.mock_manufacture_id(mid, 'dummy', oper=oper)
        else:
            logger.error("Could not parse mock from token: '%s'", token)

def list_platforms(mbeds, args):
    print(mbeds.list_manufacture_ids())

def mbeds_as_json(mbeds, args):
    print(json.dumps(mbeds.list_mbeds(unique_names=True,
                                      read_details_txt=True),
                     indent=4, sort_keys=True))

def json_by_target_id(mbeds, args):
    print(json.dumps({m['target_id']: m for m
                      in mbeds.list_mbeds(unique_names=True,
                                          read_details_txt=True)},
                     indent=4, sort_keys=True))

def json_platforms(mbeds, args):
    platforms = set()
    for d in mbeds.list_mbeds():
        platforms |= set([d['platform_name']])
    print(json.dumps(list(platforms), indent=4, sort_keys=True))

def json_platforms_ext(mbeds, args):
    platforms = defaultdict(lambda: 0)
    for d in mbeds.list_mbeds():
        platforms[d['platform_name']] += 1
    print(json.dumps(platforms, indent=4, sort_keys=True))

