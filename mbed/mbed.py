#!/usr/bin/env python

"""
mbed SDK
Copyright (c) 2011-2014 ARM Limited

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

import os
import re
import sys
import json
import optparse
import pkg_resources
from time import sleep, time
from Queue import Queue, Empty
from threading import Thread
from subprocess import Popen, PIPE

from lmtools import lmtools_factory
import host_tests.host_tests_plugins as host_tests_plugins


class ProcessObserver(Thread):
    def __init__(self, proc):
        Thread.__init__(self)
        self.proc = proc
        self.queue = Queue()
        self.daemon = True
        self.active = True
        self.start()

    def run(self):
        while self.active:
            c = self.proc.stdout.read(1)
            self.queue.put(c)

    def stop(self):
        self.active = False
        try:
            self.proc.terminate()
        except Exception, _:
            pass


class MbedTestFramework(object):
    # Test results
    TEST_RESULT_OK = "OK"
    TEST_RESULT_FAIL = "FAIL"
    TEST_RESULT_ERROR = "ERROR"
    TEST_RESULT_UNDEF = "UNDEF"
    TEST_RESULT_IOERR_COPY = "IOERR_COPY"
    TEST_RESULT_IOERR_DISK = "IOERR_DISK"
    TEST_RESULT_IOERR_SERIAL = "IOERR_SERIAL"
    TEST_RESULT_TIMEOUT = "TIMEOUT"
    TEST_RESULT_NO_IMAGE = "NO_IMAGE"

    TEST_RESULT_MAPPING = {"success" : TEST_RESULT_OK,
                           "failure" : TEST_RESULT_FAIL,
                           "error" : TEST_RESULT_ERROR,
                           "ioerr_copy" : TEST_RESULT_IOERR_COPY,
                           "ioerr_disk" : TEST_RESULT_IOERR_DISK,
                           "ioerr_serial" : TEST_RESULT_IOERR_SERIAL,
                           "timeout" : TEST_RESULT_TIMEOUT,
                           "no_image" : TEST_RESULT_NO_IMAGE,
                           "end" : TEST_RESULT_UNDEF
    }

    RE_DETECT_TESTCASE_RESULT = re.compile("\\{(" + "|".join(TEST_RESULT_MAPPING.keys()) + ")\\}")


class MbedTestFramework_GreenTea(MbedTestFramework):
    """ mbed SDK alpha1 test framework (greentea flavour)
    """

    MBEDTEST_DIRNAME = '.mbedtest'
    CONFIG_FILENAME = 'testsuite.config'
    TARGET_BINFORMAT = {
                        'default' : 'bin',
                        'nrf51822' : 'hex'
                       }
    HOST_TESTS = pkg_resources.resource_filename('host_tests', '')

    configuration = None   # Current test suite configuration (target, toolchain etc.)

    def __init__(self):
        self.create_mbedtest_dir()
        self.configuration = self.get_configuration()

    def create_mbedtest_dir(self):
        result = True
        try:
           os.mkdir('./' + self.MBEDTEST_DIRNAME)
        except:
            result = False
        return result

    def get_host_test(self):
        """ Returns name of host test for particular test
        """

    def load_ctest_testsuite(self, link_target, verbose=False):
        """ Loads CMake.CTest formatted data about tests from test directory
        """
        result = []
        add_test_pattern = 'add_test\([\w\d_-]+ \"([\w\d_-]+)\"'
        re_ptrn = re.compile(add_test_pattern)
        if link_target is not None:
            ctest_path = os.path.join(link_target, 'test', 'CTestTestfile.cmake')
            with open(ctest_path) as ctest_file:
                for line in ctest_file:
                    if line.startswith('add_test'):
                        m = re_ptrn.search(line)
                        if m and len(m.groups()) > 0:
                            if verbose:
                                print m.group(1) + '.bin'
                            result.append(os.path.join(link_target, 'test', m.group(1) + '.bin'))
        return result

    def get_json_data_from_file(self, json_spec_filename, verbose=False):
        """ Loads from file JSON formatted string to data structure
            @return JSON content, None if JSON can be loaded
        """
        result = None
        try:
            with open(json_spec_filename) as data_file:
                try:
                    result = json.load(data_file)
                except ValueError as json_error_msg:
                    result = None
                    if verbose:
                        print "Error parsing file(%s): %s" % (json_spec_filename, json_error_msg)
        except IOError as fileopen_error_msg:
            if verbose:
                print "Warning: %s" % (fileopen_error_msg)
        return result

    def get_configuration(self):
        """ Reads configuration from test suite hidden configuration directory
        """
        config_path = './' + self.MBEDTEST_DIRNAME + '/' + self.CONFIG_FILENAME
        config_data = self.get_json_data_from_file(config_path)
        if config_data is None:
            config_data = {}
        return config_data

    def set_configuration(self):
        """ Sets (update) current configuration
        """
        config_path = './' + self.MBEDTEST_DIRNAME + '/' + self.CONFIG_FILENAME
        with open(config_path, 'w') as outfile:
            json.dump(self.configuration, outfile, sort_keys=True, indent=4)

    def cli(self, opts):
        """ Executes Command Line Interface calls
        """

        if opts.list:
            path = pkg_resources.resource_filename('mbed_testsuite_meta', 'targets.json')
            lmtools = lmtools_factory()
            lmtools.manufacture_ids = lmtools.get_json_data_from_file(path)
            print lmtools

        if opts.tests:
            if not opts.link_build:
                print "Error: please use switch --link-build together with --tests to point to specific yotta target build"
                return
            # List tests available for link-target place
            self.load_ctest_testsuite(opts.link_build, verbose=True)

        if opts.target_id:
            if not opts.link_build:
                print "Error: please use switch --link-build together with --run to point to specific yotta target build"
                return

            # Run automated tests for selected link-target
            verbose = opts.verbose
            copy_method = opts.copy_method if opts.copy_method is not None else None
            loops = opts.loops if opts.loops is not None else 1
            start = time()

            tests = self.load_ctest_testsuite(opts.link_build)
            path = pkg_resources.resource_filename('mbed_testsuite_meta', 'host_tests.json')
            host_tests = self.get_json_data_from_file(path)

            target_id = opts.target_id
            path = pkg_resources.resource_filename('mbed_testsuite_meta', 'targets.json')
            lmtools = lmtools_factory()
            lmtools.manufacture_ids = lmtools.get_json_data_from_file(path)
            mbeds = lmtools.list_mbeds()
            for mbed in mbeds:
                if mbed['target_id'].startswith(target_id):

                    if mbed['mount_point'] is None:
                        print "Warning: Mount point for target %s is not detected. Skipping target testing"% (mbed['target_id'])
                        continue

                    if mbed['serial_port'] is None:
                        print "Warning: Serial port for target %s is not detected. Skipping target testing"% (mbed['target_id'])
                        continue

                    platform_name = mbed['platform_name'] if mbed['platform_name'] is not None else 'mbed_platform'
                    print "testing %s...[%s, %s] "% (platform_name, mbed['mount_point'], mbed['serial_port'])
                    for test in sorted(tests):
                        for loop in range(loops):
                            test_file_name = os.path.splitext(os.path.basename(test))[0]
                            if test_file_name in host_tests:
                                name = host_tests[test_file_name]
                                image_path = test
                                disk = mbed['mount_point']
                                port = mbed['serial_port']
                                duration = 20

                                start_host_exec_time = time()
                                single_test_result, single_test_output = self.run_host_test(name, image_path, disk, port, duration,
                                                                                            program_cycle_s=4,
                                                                                            copy_method=copy_method,
                                                                                            micro='K64F',
                                                                                            verbose=verbose)
                                elapsed_time = time() - start_host_exec_time

                                print self.print_test_result(single_test_result, test_file_name, elapsed_time, duration)
                            else:
                                print self.print_skipped_info('SKIPPED', test_file_name)
                                break
            elapsed_time = time() - start
            print
            print "Completed in %.2f sec"% (elapsed_time)

    def print_test_result(self, test_result, test_id, elapsed_time, duration, width=80):
        """ Use specific convention to print test result and related data
        """
        result = "target test '%s' executed in %.2f of %d sec"% (test_id, elapsed_time, duration)
        empty_space = width - len(result)
        result += ' ' *empty_space
        result += "[%s]"% (test_result)
        return result

    def print_skipped_info(self, test_result, test_id, width=80):
        result = "target test '%s' skipped, no automation support yet"% (test_id)
        empty_space = width - len(result)
        result += ' ' *empty_space
        result += "[%s]"% (test_result)
        return result

    def run_host_test(self, name, image_path, disk, port, duration,
                      micro=None, reset=None, reset_tout=None,
                      verbose=False, copy_method=None, program_cycle_s=None):
        """ Function creates new process with host test configured with particular test case.
            Function also is pooling for serial port activity from process to catch all data
            printed by test runner and host test during test execution
        """

        def get_char_from_queue(obs):
            """ Get character from queue safe way
            """
            try:
                c = obs.queue.get(block=True, timeout=0.5)
            except Empty, _:
                c = None
            return c

        def filter_queue_char(c):
            """ Filters out non ASCII characters from serial port
            """
            if ord(c) not in range(128):
                c = ' '
            return c

        def get_test_result(output):
            """ Parse test 'output' data
            """
            result = self.TEST_RESULT_TIMEOUT
            for line in "".join(output).splitlines():
                search_result = self.RE_DETECT_TESTCASE_RESULT.search(line)
                if search_result and len(search_result.groups()):
                    result = self.TEST_RESULT_MAPPING[search_result.groups(0)[0]]
                    break
            return result

        # print "{%s} port:%s disk:%s"  % (name, port, disk),
        cmd = ["python",
               '%s.py'% name,
               '-d', disk,
               '-f', '"%s"'% image_path,
               '-p', port,
               '-t', str(duration),
               '-C', str(program_cycle_s)]

        # Add extra parameters to host_test
        if copy_method is not None:
            cmd += ["-c", copy_method]
        if micro is not None:
            cmd += ["-m", micro]
        if reset is not None:
            cmd += ["-r", reset]
        if reset_tout is not None:
            cmd += ["-R", str(reset_tout)]

        if verbose:
            print "executing host test '" + " ".join(cmd) + "'"
            print "test start"

        proc = Popen(cmd, stdout=PIPE, cwd=self.HOST_TESTS)
        obs = ProcessObserver(proc)
        start_time = time()
        line = ''
        output = []
        while (time() - start_time) < (2 * duration):
            c = get_char_from_queue(obs)

            if c:
                if verbose:
                    sys.stdout.write(c)
                c = filter_queue_char(c)
                output.append(c)
                # Give the mbed under test a way to communicate the end of the test
                if c in ['\n', '\r']:
                    if '{end}' in line:
                        break
                    line = ''
                else:
                    line += c

        c = get_char_from_queue(obs)

        if c:
            if verbose:
                sys.stdout.write(c)
            c = filter_queue_char(c)
            output.append(c)

        if verbose:
            print "test finished"
        # Stop test process
        obs.stop()

        result = get_test_result(output)
        return result, "".join(output)


def main():
    parser = optparse.OptionParser()

    parser.add_option('-l', '--link-build',
                      dest='link_build',
                      help="Point to build directory with target specific yotta build")

    parser.add_option('', '--list',
                      dest='list',
                      default=False,
                      action="store_true",
                      help='Prints information about detected mbed enabled platforms')

    parser.add_option('-r', '--run',
                      dest='target_id',
                      help='Executes test suite automation on given mbed platfrom (by target id)')

    parser.add_option('', '--tests',
                      dest='tests',
                      default=False,
                      action="store_true",
                      help='Prints information about found tests')

    parser.add_option('', '--loops',
                      metavar="NUMBER",
                      type="int",
                      dest='loops',
                      help='Set no. of loops per test')

    copy_methods = host_tests_plugins.get_plugin_caps('CopyMethod')
    copy_methods_str = "Plugin support: " + ', '.join(copy_methods)

    parser.add_option('-v', '--verbose',
                      dest='verbose',
                      default=False,
                      action="store_true",
                      help='Verbose mode prints test case output received from target under test')

    parser.description = """This script allows you to run mbed defined test cases for particular MCU(s) and corresponding toolchain(s)."""
    parser.epilog = """"""

    (opts, args) = parser.parse_args()

    mbed_testsuite = MbedTestFramework_GreenTea()
    mbed_testsuite.cli(opts)
