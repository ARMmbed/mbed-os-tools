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
import optparse
import platform

from .lstools_win7 import MbedLsToolsWin7
from .lstools_linux_generic import MbedLsToolsLinuxGeneric
from .lstools_darwin import MbedLsToolsDarwin

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
        if mbed_os == 'Windows7': result = MbedLsToolsWin7(**kwargs)
        elif mbed_os == 'LinuxGeneric': result = MbedLsToolsLinuxGeneric(**kwargs)
        elif mbed_os == 'Darwin': result = MbedLsToolsDarwin(**kwargs)
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


def cmd_parser_setup():
    """! Configure CLI (Command Line OPtions) options

    @return Returns OptionParser's tuple of (options, arguments)

    @details Add new command line options here to control 'mbedls' command line iterface
    """
    parser = optparse.OptionParser()

    parser.add_option('-s', '--simple',
                      dest='simple',
                      default=False,
                      action="store_true",
                      help='Parser friendly verbose mode')

    parser.add_option('-l', '--list',
                      dest='list_platforms',
                      default=False,
                      action="store_true",
                      help='List all platforms and corresponding TargetID values mapped by mbed-ls')

    parser.add_option('-m', '--mock',
                      dest='mock_platform',
                      help='Add locally manufacturers id and platform name. Example --mock=12B4:NEW_PLATFORM')

    parser.add_option('-j', '--json',
                      dest='json',
                      default=False,
                      action="store_true",
                      help='JSON formatted list of targets detailed information')

    parser.add_option('-J', '--json-by-target-id',
                      dest='json_by_target_id',
                      default=False,
                      action="store_true",
                      help='JSON formatted dictionary ordered by TargetID of targets detailed information')

    parser.add_option('-p', '--json-platforms',
                      dest='json_platforms',
                      default=False,
                      action="store_true",
                      help='JSON formatted list of available platforms')

    parser.add_option('-P', '--json-platforms-ext',
                      dest='json_platforms_ext',
                      default=False,
                      action="store_true",
                      help='JSON formatted dictionary of platforms count')

    parser.add_option('', '--skip-retarget',
                      dest='skip_retarget',
                      default=False,
                      action="store_true",
                      help='Ignores file ./mbedls.json with retarget data')

    parser.add_option('-u', '--list-unmounted',
                      dest='list_unmounted',
                      default=False,
                      action='store_true',
                      help='List unmounted mbeds in addition to ones that are mounted.')

    parser.add_option('-d', '--debug',
                      dest='debug',
                      default=False,
                      action="store_true",
                      help='Outputs extra debug information')

    parser.add_option('', '--version',
                      dest='version',
                      default=False,
                      action="store_true",
                      help='Prints package version and exits')

    (opts, args) = parser.parse_args()
    return (opts, args)


def mbedls_main():
    """! Function used to drive CLI (command line interface) application
    @return Function exits with success code
    @details Function exits back to command line with ERRORLEVEL
    """

    def get_mbedls_version():
        """! Get mbed-ls Python module version string """
        import pkg_resources  # part of setuptools
        version = pkg_resources.require("mbed-ls")[0].version
        return version

    (opts, args) = cmd_parser_setup()

    root_logger = logging.getLogger("")
    try:
        import colorlog
        colorlog.basicConfig(
            format='%(log_color)s%(levelname)s%(reset)s:%(name)s:%(message)s')
    except ImportError:
        logging.basicConfig()
    if opts.debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
    logger.debug("mbed-ls ver. %s", get_mbedls_version())
    logger.debug("host: %s",  str((mbed_lstools_os_info())))

    mbeds = create(skip_retarget=opts.skip_retarget,
                   list_unmounted=opts.list_unmounted,
                   force_mock=opts.mock_platform)

    if mbeds is None:
        logger.critical('This platform is not supported! Pull requests welcome at github.com/ARMmbed/mbed-ls')
        sys.exit(-1)


    if opts.list_platforms:
        print(mbeds.list_manufacture_ids())
        sys.exit(0)

    if opts.mock_platform:
        if opts.mock_platform == '*':
            if opts.json:
                print(json.dumps(mbeds.mock_read(), indent=4))

        for token in opts.mock_platform.split(','):
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
        if opts.json:
            print(json.dumps(mbeds.mock_read(), indent=4))

    elif opts.json:
        print(json.dumps(mbeds.list_mbeds_ext(), indent=4, sort_keys=True))

    elif opts.json_by_target_id:
        print(json.dumps(mbeds.list_mbeds_by_targetid(), indent=4, sort_keys=True))

    elif opts.json_platforms:
        print(json.dumps(mbeds.list_platforms(), indent=4, sort_keys=True))

    elif opts.json_platforms_ext:
        print(json.dumps(mbeds.list_platforms_ext(), indent=4, sort_keys=True))

    elif opts.version:
        print(get_mbedls_version())

    else:
        print(mbeds.get_string(border=not opts.simple, header=not opts.simple))

    logger.debug("Return code: %d", mbeds.ERRORLEVEL_FLAG)

    sys.exit(mbeds.ERRORLEVEL_FLAG)
