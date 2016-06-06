"""
mbed SDK
Copyright (c) 2011-2016 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""


"""! @package mbed-host-tests

Flash, reset and  perform host supervised tests on mbed platforms.
Write your own programs (import this package) or use 'mbedhtrun' command line tool instead.

"""


import os
import imp
import inspect
from os import listdir
from os.path import isfile, join, abspath
from optparse import OptionParser

from mbed_host_tests import host_tests_plugins
from mbed_host_tests.host_tests_registry import HostRegistry
from mbed_host_tests.host_tests import BaseHostTest, event_callback

# Host test supervisors
from  mbed_host_tests.host_tests.echo import EchoTest
from  mbed_host_tests.host_tests.rtc_auto import RTCTest
from  mbed_host_tests.host_tests.hello_auto import HelloTest
from  mbed_host_tests.host_tests.detect_auto import DetectPlatformTest
from  mbed_host_tests.host_tests.wait_us_auto import WaitusTest
from  mbed_host_tests.host_tests.default_auto import DefaultAuto
from  mbed_host_tests.host_tests.dev_null_auto import DevNullTest

# Populate registry with supervising objects
HOSTREGISTRY = HostRegistry()
HOSTREGISTRY.register_host_test("echo", EchoTest())
HOSTREGISTRY.register_host_test("default", DefaultAuto())
HOSTREGISTRY.register_host_test("rtc_auto", RTCTest())
HOSTREGISTRY.register_host_test("hello_auto", HelloTest())
HOSTREGISTRY.register_host_test("detect_auto", DetectPlatformTest())
HOSTREGISTRY.register_host_test("default_auto", DefaultAuto())
HOSTREGISTRY.register_host_test("wait_us_auto", WaitusTest())
HOSTREGISTRY.register_host_test("dev_null_auto", DevNullTest())

###############################################################################
# Functional interface for test supervisor registry
###############################################################################


def get_host_test(ht_name):
    """! Fetches host test object from HOSTREGISTRY
    @param ht_name Host test name
    @return Returns registered host test supervisor.
            If host test is not registered by name function returns None.
    """
    return HOSTREGISTRY.get_host_test(ht_name)

def is_host_test(ht_name):
    """! Checks if host test supervisor is registered in host test registry.
    @param ht_name Host test name
    @return If host test supervisor is registered returns True otherwise False.
    """
    return HOSTREGISTRY.is_host_test(ht_name)

def get_host_test_list():
    """! Returns list of host test names and its classes
    @return Dictionary of {host_test_name : __class__}
    """
    result = {}
    for ht in sorted(HOSTREGISTRY.HOST_TESTS.keys()):
        result[ht] = HOSTREGISTRY.HOST_TESTS[ht].__class__
    return result

def get_plugin_caps(methods=None):
    if not methods:
        methods = ['CopyMethod', 'ResetMethod']
    result = {}
    for method in methods:
        result[method] = host_tests_plugins.get_plugin_caps(method)
    return result

def print_ht_list(verbose=False):
    """! Prints list of registered host test classes (by name)
        @Detail For devel & debug purposes
    """
    from prettytable import PrettyTable
    column_names = ['name', 'class', 'origin']
    pt = PrettyTable(column_names)
    for column in column_names:
        pt.align[column] = 'l'

    # Opiortunistic approach: always try to add current ./test/host_tests
    enum_host_tests('./test/host_tests', verbose=verbose)

    ht_str_len = 0
    cls_str_len = 0
    for ht in HOSTREGISTRY.HOST_TESTS:
        cls_str = str(HOSTREGISTRY.HOST_TESTS[ht].__class__)

        if len(ht) > ht_str_len: ht_str_len = len(ht)
        if len(cls_str) > cls_str_len: cls_str_len = len(cls_str)
    for ht in sorted(HOSTREGISTRY.HOST_TESTS.keys()):
        cls_str = str(HOSTREGISTRY.HOST_TESTS[ht].__class__)
        script_path_str = HOSTREGISTRY.HOST_TESTS[ht].script_location if HOSTREGISTRY.HOST_TESTS[ht].script_location else 'mbed-host-tests'
        row = [ht, cls_str, script_path_str]
        pt.add_row(row)
    print pt.get_string()

def enum_host_tests(path, verbose=False):
    """ Enumerates and registers locally stored host tests
        Host test are derived from mbed_host_tests.BaseHostTest classes
    """
    if verbose:
        print "HOST: Inspecting '%s' for local host tests..."% abspath(path)

    if path:
        # Normalize path and check proceed if directory 'path' exist
        path = path.strip('"')  # Remove quotes from command line
        if os.path.exists(path) and os.path.isdir(path):
            # Listing Python tiles within path directory
            host_tests_list = [f for f in listdir(path) if isfile(join(path, f))]
            for ht in host_tests_list:
                if ht.endswith(".py"):
                    abs_path = abspath(join(path, ht))
                    try:
                        mod = imp.load_source(ht[:-3], abs_path)
                    except Exception as e:
                        print "HOST: Error! While loading local host test module '%s'"% abs_path
                        print "HOST: %s"% str(e)
                        continue
                    if verbose:
                        print "HOST: Loading module '%s': "% (ht), str(mod)

                    for mod_name, mod_obj in inspect.getmembers(mod):
                        if inspect.isclass(mod_obj):
                            #if verbose:
                            #    print 'HOST: Class found:', str(mod_obj), type(mod_obj)
                            if issubclass(mod_obj, BaseHostTest) and str(mod_obj) != str(BaseHostTest):
                                host_test_name = ht[:-3]
                                if mod_obj.name:
                                    host_test_name = mod_obj.name
                                host_test_cls = mod_obj
                                host_test_cls.script_location = abs_path
                                if verbose:
                                    print "HOST: Found host test implementation: %s -|> %s"% (str(mod_obj), str(BaseHostTest))
                                    print "HOST: Registering '%s' as '%s'"% (str(host_test_cls), host_test_name)
                                HOSTREGISTRY.register_host_test(host_test_name, host_test_cls())

def init_host_test_cli_params():
    """! Function creates CLI parser object and returns populated options object.
    @return Function returns 'options' object returned from OptionParser class
    @details Options object later can be used to populate host test selector script.
    """
    parser = OptionParser()

    parser.add_option("-m", "--micro",
                      dest="micro",
                      help="Target microcontroller name",
                      metavar="MICRO")

    parser.add_option("-p", "--port",
                      dest="port",
                      help="Serial port of the target",
                      metavar="PORT")

    parser.add_option("-d", "--disk",
                      dest="disk",
                      help="Target disk (mount point) path",
                      metavar="DISK_PATH")

    parser.add_option("-t", "--target-id",
                      dest="target_id",
                      help="Unique Target Id or mbed platform",
                      metavar="TARGET_ID")

    parser.add_option("-f", "--image-path",
                      dest="image_path",
                      help="Path with target's binary image",
                      metavar="IMAGE_PATH")

    copy_methods_str = "Plugin support: " + ', '.join(host_tests_plugins.get_plugin_caps('CopyMethod'))

    parser.add_option("-c", "--copy",
                      dest="copy_method",
                      help="Copy (flash the target) method selector. " + copy_methods_str,
                      metavar="COPY_METHOD")

    reset_methods_str = "Plugin support: " + ', '.join(host_tests_plugins.get_plugin_caps('ResetMethod'))

    parser.add_option("-r", "--reset",
                      dest="forced_reset_type",
                      help="Forces different type of reset. " + reset_methods_str)

    parser.add_option("-C", "--program_cycle_s",
                      dest="program_cycle_s",
                      help="Program cycle sleep. Define how many seconds you want wait after copying binary onto target",
                      type="float",
                      metavar="PROGRAM_CYCLE_S")

    parser.add_option("-R", "--reset-timeout",
                      dest="forced_reset_timeout",
                      metavar="NUMBER",
                      type="int",
                      help="When forcing a reset using option -r you can set up after reset idle delay in seconds")

    parser.add_option("-e", "--enum-host-tests",
                      dest="enum_host_tests",
                      help="Define directory with local host tests")

    parser.add_option('', '--test-cfg',
                      dest='json_test_configuration',
                      help='Pass to host test class data about host test configuration')

    parser.add_option('', '--list',
                      dest='list_reg_hts',
                      default=False,
                      action="store_true",
                      help='Prints registered host test and exits')

    parser.add_option('', '--plugins',
                      dest='list_plugins',
                      default=False,
                      action="store_true",
                      help='Prints registered plugins and exits')

    parser.add_option('', '--run',
                      dest='run_binary',
                      default=False,
                      action="store_true",
                      help='Runs binary image on target (workflow: flash, reset, output console)')

    parser.add_option('', '--skip-flashing',
                      dest='skip_flashing',
                      default=False,
                      action="store_true",
                      help='Skips use of copy/flash plugin. Note: target will not be reflashed')

    parser.add_option('', '--skip-reset',
                      dest='skip_reset',
                      default=False,
                      action="store_true",
                      help='Skips use of reset plugin. Note: target will not be reset')

    parser.add_option('-P', '--pooling-timeout',
                      dest='pooling_timeout',
                      default=60,
                      metavar="NUMBER",
                      type="int",
                      help='Timeout in sec for mbed-ls mount point and serial port readiness. Default 60 sec')

    parser.add_option('-b', '--send-break',
                      dest='send_break_cmd',
                      default=False,
                      action="store_true",
                      help='Send reset signal to board on specified port (-p PORT) and print serial output. You can combine this with (-r RESET_TYPE) switch')

    parser.add_option('-v', '--verbose',
                      dest='verbose',
                      default=False,
                      action="store_true",
                      help='More verbose mode')

    parser.add_option('', '--version',
                      dest='version',
                      default=False,
                      action="store_true",
                      help='Prints package version and exits')

    parser.description = """Flash, reset and perform host supervised tests on mbed platforms"""
    parser.epilog = """Example: mbedhtrun -d E: -p COM5 -f "test.bin" -C 4 -c shell -m K64F"""

    (options, _) = parser.parse_args()
    return options
