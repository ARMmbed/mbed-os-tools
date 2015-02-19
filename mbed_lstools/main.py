#!/usr/bin/env python


import os
import sys
import json
import optparse
import platform

from lstools_win7 import MbedLsToolsWin7
from lstools_ubuntu import MbedLsToolsUbuntu
from lstools_darwin import MbedLsToolsDarwin


def create():
    """ Factory producing mbed-lstools depending on OS it is working on
    """
    result = None
    mbed_os = mbed_os_support()
    if mbed_os is not None:
        if mbed_os == 'Windows7': result = MbedLsToolsWin7()
        elif mbed_os == 'Ubuntu': result = MbedLsToolsUbuntu()
        elif mbed_os == 'Ubuntu': result = MbedLsToolsUbuntu()
        elif mbed_os == 'Darwin': result = MbedLsToolsDarwin()
    return result

def mbed_os_support():
    """ Function return True if host OS supports mbed-enabled devices detections procedures.
        Returns False if this feature is not implemented.
    """
    result = None
    os_info = mbed_lstools_os_info()
    if (os_info[0] == 'nt' and os_info[1] == 'Windows'):
        result = 'Windows7'
    elif (os_info[0] == 'posix' and os_info[1] == 'Linux' and ('Ubuntu' in os_info[3])):
        result = 'Ubuntu'
    elif (os_info[0] == 'posix' and os_info[1] == 'Darwin'):
        result = 'Darwin'
    return result

def mbed_lstools_os_info():
    """ Returns information about running OS
    """
    result = (os.name,
              platform.system(),
              platform.release(),
              platform.version(),
              sys.platform)
    return result

def cmd_parser_setup():
    """ Configure command line options
    """
    parser = optparse.OptionParser()

    parser.add_option('-s', '--simple',
                      dest='simple',
                      default=False,
                      action="store_true",
                      help='Parser friendly verbose mode')

    parser.add_option('', '--json',
                      dest='json',
                      default=False,
                      action="store_true",
                      help='JSON formatted output')

    (opts, args) = parser.parse_args()
    return (opts, args)


def mbedls_main():
    """ Function used to drive command line interface for this mbed-lstools library.
        This function provides output for 'mbedls' command.
    """
    (opts, args) = cmd_parser_setup()
    mbeds = create()

    if mbeds is None:
        sys.stderr.write('This platform is not supported! Pull requests welcome at github.com/ARMmbed/mbed-ls\n')
        sys.exit(-1)

    if opts.json:
        mbeds_data = mbeds.list_mbeds()
        print json.dumps(mbeds_data, indent=4, sort_keys=True)
    else:
        print mbeds.get_string(border=not opts.simple, header=not opts.simple)
