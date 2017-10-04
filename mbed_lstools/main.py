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
import argparse
import platform
from collections import defaultdict
import logging

logger = logging.getLogger("mbedls.main")


def create(**kwargs):
    """! Factory used to create host OS specific mbed-lstools object

    :param kwargs: To pass arguments transparently to MbedLsToolsBase class.
    @return Returns MbedLsTools object or None if host OS is not supported

    @details Function detects host OS. Each host platform should be ported to support new host platform (OS)
    """
    result = None
    mbed_os = mbed_os_support()
    if mbed_os is not None:
        if mbed_os == 'Windows7':
            from .lstools_win7 import MbedLsToolsWin7
            result = MbedLsToolsWin7(**kwargs)
        elif mbed_os == 'LinuxGeneric':
            from .lstools_linux_generic import MbedLsToolsLinuxGeneric
            result = MbedLsToolsLinuxGeneric(**kwargs)
        elif mbed_os == 'Darwin':
            from .lstools_darwin import MbedLsToolsDarwin
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


def get_version():
    """! Get mbed-ls Python module version string """
    import pkg_resources  # part of setuptools
    return pkg_resources.require("mbed-ls")[0].version

def print_version(mbeds, args):
    print(get_version())

def print_mbeds(mbeds, args, simple):
    devices = mbeds.list_mbeds(unique_names=True, read_details_txt=True)
    if devices:
        from prettytable import PrettyTable
        columns = ['platform_name', 'platform_name_unique', 'mount_point',
                    'serial_port', 'target_id', 'daplink_version']
        pt = PrettyTable(columns)
        for d in devices:
            pt.add_row([d.get(col, None) or 'unknown' for col in columns])
        print(pt.get_string(border=not simple, header=not simple,
                            padding_width=1, sortby='platform_name_unique'))

def print_table(mbeds, args):
    return print_mbeds(mbeds, args, False)

def print_simple(mbeds, args):
    return print_mbeds(mbeds, args, True)

def mock_platform(mbeds, args):
    for token in args.mock_platform.split(','):
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

def parse_cli():
    """! Parse the command line

    @return Retrun a namespace that contains:
     * command - python function to run
     * skip_retarget - bool indicting to skip retargeting
     * list_unmounted - list boards that are not mounted
     * debug - turn on debug logging
    """
    parser = argparse.ArgumentParser()
    parser.set_defaults(command=print_table)

    commands = parser.add_mutually_exclusive_group()
    commands.add_argument(
        '-s', '--simple', dest='command', action='store_const',
        const=print_simple, help='Parser friendly verbose mode')
    commands.add_argument(
        '-j', '--json', dest='command', action='store_const',
        const=mbeds_as_json,
        help='JSON formatted list of targets detailed information')
    commands.add_argument(
        '-J', '--json-by-target-id', dest='command', action='store_const',
        const=json_by_target_id,
        help='JSON formatted dictionary ordered by TargetID of targets detailed information')
    commands.add_argument(
        '-p', '--json-platforms', dest='command', action='store_const',
        const=json_platforms,
        help='JSON formatted list of available platforms')
    commands.add_argument(
        '-P', '--json-platforms-ext', dest='command', action='store_const',
        const=json_platforms_ext,
        help='JSON formatted dictionary of platforms count')
    commands.add_argument(
        '-l', '--list', dest='command', action='store_const', const=list_platforms,
        help='List all platforms and corresponding TargetID values mapped by mbed-ls')
    commands.add_argument(
        '--version', dest='command', action='store_const', const=print_version,
        help='Prints package version and exits')
    commands.add_argument(
        '-m', '--mock', dest='command', action='store_const', const=mock_platform,
        help='Add locally manufacturers id and platform name. Example --mock=12B4:NEW_PLATFORM')

    parser.add_argument(
        '--skip-retarget', dest='skip_retarget', default=False,
        action="store_true",
        help='Ignores file ./mbedls.json with retarget data')
    parser.add_argument(
        '-u', '--list-unmounted', dest='list_unmounted', default=False,
        action='store_true',
        help='List unmounted mbeds in addition to ones that are mounted.')
    parser.add_argument(
        '-d', '--debug', dest='debug', default=False, action="store_true",
        help='Outputs extra debug information')

    return parser.parse_args()

def mbedls_main():
    """! Function used to drive CLI (command line interface) application
    @return Function exits with success code
    """
    root_logger = logging.getLogger("")
    try:
        import colorlog
        colorlog.basicConfig(
            format='%(log_color)s%(levelname)s%(reset)s:%(name)s:%(message)s')
    except ImportError:
        logging.basicConfig()

    args = parse_cli()

    if args.debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
    logger.debug("mbed-ls ver. %s", get_version())
    logger.debug("host: %s",  str(mbed_lstools_os_info()))

    mbeds = create(skip_retarget=args.skip_retarget,
                   list_unmounted=args.list_unmounted,
                   force_mock=args.command is mock_platform)

    if mbeds is None:
        logger.critical('This platform is not supported! Pull requests welcome at github.com/ARMmbed/mbed-ls')
        sys.exit(-1)

    ret_code = args.command(mbeds, args)
    if not ret_code:
        ret_code = 0

    logger.debug("Return code: %d", ret_code)

    sys.exit(ret_code)
