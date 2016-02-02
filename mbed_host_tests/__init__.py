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

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""


"""! @package mbed-host-tests

Flash, reset and  perform host supervised tests on mbed platforms.
Write your own programs (import this package) or use 'mbedhtrun' command line tool instead.

"""

import os
import sys
import imp
import json
import inspect
from multiprocessing import Process, Queue, Lock

from os import listdir
from os.path import isfile, join, abspath
from time import sleep, time
from optparse import OptionParser

import host_tests_plugins
from host_tests_registry import HostRegistry
from host_tests import BaseHostTest
from host_tests_conn_proxy import conn_process
from host_tests_conn_proxy import HtrunLogger

# Host test supervisors
from host_tests.echo import EchoTest
from host_tests.rtc_auto import RTCTest
from host_tests.stdio_auto import StdioTest
from host_tests.hello_auto import HelloTest
from host_tests.detect_auto import DetectPlatformTest
from host_tests.wait_us_auto import WaitusTest
from host_tests.default_auto import DefaultAuto
from host_tests.dev_null_auto import DevNullTest
from host_tests.run_only_auto import RunBinaryOnlyAuto
from host_tests.tcpecho_server_auto import TCPEchoServerTest
from host_tests.udpecho_server_auto import UDPEchoServerTest
from host_tests.tcpecho_client_auto import TCPEchoClientTest
from host_tests.udpecho_client_auto import UDPEchoClientTest
from host_tests.test_socket_server_udp import UDPSocketServerEchoExtTest
from host_tests.test_socket_server_tcp import TCPSocketServerEchoExtTest

# Basic host test functionality
from host_tests_runner.host_test import DefaultTestSelectorBase

# Populate registry with supervising objects
HOSTREGISTRY = HostRegistry()
HOSTREGISTRY.register_host_test("echo", EchoTest())
HOSTREGISTRY.register_host_test("default", DefaultAuto())
HOSTREGISTRY.register_host_test("rtc_auto", RTCTest())
HOSTREGISTRY.register_host_test("hello_auto", HelloTest())
HOSTREGISTRY.register_host_test("stdio_auto", StdioTest())
HOSTREGISTRY.register_host_test("detect_auto", DetectPlatformTest())
HOSTREGISTRY.register_host_test("default_auto", DefaultAuto())
HOSTREGISTRY.register_host_test("wait_us_auto", WaitusTest())
HOSTREGISTRY.register_host_test("dev_null_auto", DevNullTest())
HOSTREGISTRY.register_host_test("run_binary_auto", RunBinaryOnlyAuto())
HOSTREGISTRY.register_host_test("tcpecho_server_auto", TCPEchoServerTest())
HOSTREGISTRY.register_host_test("udpecho_server_auto", UDPEchoServerTest())
HOSTREGISTRY.register_host_test("tcpecho_client_auto", TCPEchoClientTest())
HOSTREGISTRY.register_host_test("udpecho_client_auto", UDPEchoClientTest())
HOSTREGISTRY.register_host_test("test_socket_server_udp", UDPSocketServerEchoExtTest())
HOSTREGISTRY.register_host_test("test_socket_server_tcp", TCPSocketServerEchoExtTest())

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

def flash_dev(disk=None,
              image_path=None,
              copy_method='default',
              port=None,
              program_cycle_s=0):
    """! Flash device using pythonic interface
    @param disk Switch -d <disk>
    @param image_path Switch -f <image_path>
    @param copy_method Switch -c <copy_method> (default: shell)
    @param port Switch -p <port>
    """
    if copy_method == 'default':
        copy_method = 'shell'
    result = False
    result = host_tests_plugins.call_plugin('CopyMethod',
                                            copy_method,
                                            image_path=image_path,
                                            serial=port,
                                            destination_disk=disk)
    sleep(program_cycle_s)
    return result

def reset_dev(port=None,
              disk=None,
              reset_type='default',
              reset_timeout=1,
              serial_port=None,
              baudrate=115200,
              timeout=1,
              verbose=False):
    """! Reset device using pythonic interface
    @param port Switch -p <port>
    @param disk Switch -d <disk>
    @param reset_type Switch -r <reset_type>
    @param reset_timeout Switch -R <reset_timeout>
    @param serial_port Serial port handler, set to None if you want this function to open serial

    @param baudrate Serial port baudrate
    @param timeout Serial port timeout
    @param verbose Verbose mode
    """
    from serial import Serial

    result = False
    if not serial_port:
        try:
            with Serial(port, baudrate=baudrate, timeout=timeout) as serial_port:
                result = host_tests_plugins.call_plugin('ResetMethod',
                                                        reset_type,
                                                        serial=serial_port,
                                                        disk=disk)
            sleep(reset_timeout)
        except Exception as e:
            if verbose:
                print "%s" % (str(e))
            result = False
    return result

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
                                if verbose:
                                    print "HOST: Found host test implementation: %s -|> %s"% (str(mod_obj), str(BaseHostTest))
                                    print "HOST: Registering '%s' as '%s'"% (str(host_test_cls), host_test_name)
                                HOSTREGISTRY.register_host_test(host_test_name, host_test_cls())


class DefaultTestSelector(DefaultTestSelectorBase):
    """ Select default host_test supervision (replaced after auto detection)
    """
    test_supervisor = get_host_test("default")

    def __init__(self, options):
        """! ctor
        """
        self.options = options

        self.prn_lock = Lock()
        self.logger = HtrunLogger(self.prn_lock)

        # Handle extra command from
        if options:
            if options.enum_host_tests:
                path = self.options.enum_host_tests
                enum_host_tests(path, verbose=options.verbose)

            if options.list_reg_hts:    # --list option
                self.print_ht_list()
                sys.exit(0)

            if options.list_plugins:    # --plugins option
                host_tests_plugins.print_plugin_info()
                sys.exit(0)

            if options.version:         # --version
                import pkg_resources    # part of setuptools
                version = pkg_resources.require("mbed-host-tests")[0].version
                print version
                sys.exit(0)

            if options.send_break_cmd:  # -b with -p PORT (and optional -r RESET_TYPE)
                self.handle_send_break_cmd(port=options.port,
                    disk=options.disk,
                    reset_type=options.forced_reset_type,
                    verbose=options.verbose)
                sys.exit(0)

        DefaultTestSelectorBase.__init__(self, options)

        # Following flag is to indicate to this selector that parent process wants it to abort.
        # It would to set by self.abort() by parent_monitor_thread() thread in mbedhtrun.py.
        # Since this selector does not employ a loop and immediate exit is not necessary we don't need locking around it
        self.aborted = False

    def print_ht_list(self):
        """! Prints list of registered host test classes (by name)
            @Detail For devel & debug purposes
        """
        str_len = 0
        for ht in HOSTREGISTRY.HOST_TESTS:
            if len(ht) > str_len: str_len = len(ht)
        for ht in sorted(HOSTREGISTRY.HOST_TESTS.keys()):
            print "'%s'%s : %s()" % (ht, ' '*(str_len - len(ht)), HOSTREGISTRY.HOST_TESTS[ht].__class__)

    def handle_send_break_cmd(self, port, disk, reset_type=None, baudrate=115200, timeout=1, verbose=False):
        """! Resets platforms and prints serial port output
            @detail Mix with switch -r RESET_TYPE and -p PORT for versatility
        """
        from serial import Serial

        if not reset_type:
            reset_type = 'default'

        port_config = port.split(':')
        if len(port_config) == 2:
            # -p COM4:115200
            port = port_config[0]
            baudrate = int(port_config[1])
        elif len(port_config) == 3:
            # -p COM4:115200:0.5
            port = port_config[0]
            baudrate = int(port_config[1])
            timeout = float(port_config[2])

        if verbose:
            print "mbedhtrun: serial port configuration: %s:%s:%s"% (port, str(baudrate), str(timeout))

        try:
            serial_port = Serial(port, baudrate=baudrate, timeout=timeout)
        except Exception as e:
            print "mbedhtrun: %s" % (str(e))
            print json.dumps({
                "port" : port,
                "disk" : disk,
                "baudrate" : baudrate,
                "timeout" : timeout,
                "reset_type" : reset_type,
                }, indent=4)
            return False

        serial_port.flush()
        # Reset using one of the plugins
        result = host_tests_plugins.call_plugin('ResetMethod', reset_type, serial=serial_port, disk=disk)
        if not result:
            print "mbedhtrun: reset plugin failed"
            print json.dumps({
                "port" : port,
                "disk" : disk,
                "baudrate" : baudrate,
                "timeout" : timeout,
                "reset_type" : reset_type
                }, indent=4)
            return False

        print "mbedhtrun: serial dump started (use ctrl+c to break)"
        try:
            while True:
                test_output = serial_port.read(512)
                if test_output:
                    sys.stdout.write('%s'% test_output)
                if "{end}" in test_output:
                    if verbose:
                        print
                        print "mbedhtrun: stopped (found '{end}' terminator)"
                    break
        except KeyboardInterrupt:
            print "ctrl+c break"

        serial_port.close()
        return True

    def execute(self):
        """! Test runner for host test.

        @return This function doesn't return. It prints result on serial port from host test supervisor.
                Test result string is cough by test framework

        @details This function will start executing test and forward test result via serial port
                 to test suite. This function is sensitive to work-flow flags such as --skip-flashing,
                 --skip-reset etc.
                 First function will flash device with binary, initialize serial port for communication,
                 reset target. On serial port handshake with test case will be performed. It is when host
                 test reads property data from serial port (sent over serial port).
                 At the end of the procedure proper host test (defined in set properties) will be executed
                 and test execution timeout will be measured.
        """
        # Copy image to device
        if self.options.skip_flashing is False:
            self.logger.prn_inf("copy image onto target...")
            result = self.mbed.copy_image()
            if not result:
                self.print_result(self.RESULT_IOERR_COPY)
                return  # No need to continue, we can't flash device
        else:
            self.logger.prn_inf("copy image onto target... SKIPPED!")

        # Initialize and open target's serial port (console)

        result = self.run_test()
        if result == True:
            self.print_result(self.RESULT_SUCCESS)
        elif result == False:
            self.print_result(self.RESULT_FAILURE)
        elif result is None:
            self.print_result(self.RESULT_ERROR)

    def run_test(self):
        result = None
        timeout_duration = 10       # Default test case timeout
        event_queue = Queue()       # Events from DUT to host
        dut_event_queue = Queue()   # Events from host to DUT {k;v}

        callbacks = {
            "__notify_prn" : lambda k, v, t : self.logger.prn_inf(v)
        }

        # if True we will allow host test to consume all events after test is funished
        callbacks_consume = True
        self.test_supervisor = None

        config = {
            "digest" : "serial",
            "port" : self.mbed.port,
            "baudrate" : self.mbed.serial_baud,
            "program_cycle_s" : self.options.program_cycle_s
            }

        self.logger.prn_inf("starting host test process...")
        start_time = time()
        args = (event_queue, dut_event_queue, self.prn_lock, config)
        p = Process(target=conn_process, args=args)
        p.deamon = True
        p.start()

        consume_preamble_events = True
        while (time() - start_time) < timeout_duration:
            # Handle default events like timeout, host_test_name, ...
            if event_queue.qsize():
                (key, value, timestamp) = event_queue.get()

                if consume_preamble_events:
                    if key == 'timeout':
                        self.logger.prn_inf("setting timeout to: %d sec"% int(value))
                        start_time = time()
                        timeout_duration = int(value) # New timeout
                    elif key == 'host_test_name':
                        self.test_supervisor = get_host_test(value)
                        if self.test_supervisor:
                            self.test_supervisor.event_queue = event_queue
                            self.test_supervisor.dut_event_queue = dut_event_queue
                            self.test_supervisor.setup()
                            self.logger.prn_inf("host test setup() call...")
                            if self.test_supervisor.callbacks:
                                callbacks.update(self.test_supervisor.callbacks)
                                self.logger.prn_inf("CALLBACKs updated")
                            else:
                                self.logger.prn_wrn("no CALLBACKs specified by host test")
                            self.logger.prn_inf("host test detected: %s"% value)
                        else:
                            self.logger.prn_err("host test not detected: %s"% value)
                        consume_preamble_events = False
                    elif key == 'sync':
                        self.logger.prn_inf("sync KV found, uuid=%s, timestamp=%f"% (str(value), timestamp))
                    else:
                        self.logger.prn_err("orphan event in preamble phase: {{%s;%s}}, timestamp=%f"% (key, str(value), timestamp))
                else:
                    if key == '__notify_complete':
                        self.logger.prn_inf(key)
                        callbacks_consume = value
                        break
                    elif key in callbacks:
                        callbacks[key](key, value, timestamp)
                    else:
                        self.logger.prn_err("orphan event in main phase: {{%s;%s}}, timestamp=%f"% (key, str(value), timestamp))

        time_duration = time() - start_time
        self.logger.prn_inf("test suite run finished after %.2f..."% time_duration)

        p.terminate()
        self.logger.prn_inf("exited with code: %s"% str(p.exitcode))

        # Callbacks...
        self.logger.prn_inf("%d events in queue"% event_queue.qsize())

        if self.test_supervisor:
            if callbacks_consume:
                # We are consuming all remaining events if requested
                while event_queue.qsize():
                    (key, value, timestamp) = event_queue.get()
                    if key in callbacks:
                        callbacks[key](key, value, timestamp)
                    else:
                        self.logger.prn_inf(">>> orphan event: {{%s;%s}}, timestamp=%f"% (key, str(value), timestamp))

            result = self.test_supervisor.test()
            self.logger.prn_inf("Host test test() result: %s"% str(result))
            self.test_supervisor.teardown()

        return result

    def abort(self):
        """
        Handler for abort instruction from mbed greentea.

        :return:
        """
        pass

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
