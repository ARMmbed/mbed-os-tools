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

Author: Przemyslaw Wirkus <Przemyslaw.wirkus@arm.com>
"""

import re
import sys
from time import time
from subprocess import call, Popen, PIPE, STDOUT

from mbed_greentea.mbed_greentea_log import gt_logger


# Return codes for test script
TEST_RESULT_OK = "OK"
TEST_RESULT_FAIL = "FAIL"
TEST_RESULT_ERROR = "ERROR"
TEST_RESULT_UNDEF = "UNDEF"
TEST_RESULT_IOERR_COPY = "IOERR_COPY"
TEST_RESULT_IOERR_DISK = "IOERR_DISK"
TEST_RESULT_IOERR_SERIAL = "IOERR_SERIAL"
TEST_RESULT_TIMEOUT = "TIMEOUT"
TEST_RESULT_NO_IMAGE = "NO_IMAGE"
TEST_RESULT_MBED_ASSERT = "MBED_ASSERT"
TEST_RESULT_BUILD_FAILED = "BUILD_FAILED"

TEST_RESULTS = [TEST_RESULT_OK,
                TEST_RESULT_FAIL,
                TEST_RESULT_ERROR,
                TEST_RESULT_UNDEF,
                TEST_RESULT_IOERR_COPY,
                TEST_RESULT_IOERR_DISK,
                TEST_RESULT_IOERR_SERIAL,
                TEST_RESULT_TIMEOUT,
                TEST_RESULT_NO_IMAGE,
                TEST_RESULT_MBED_ASSERT,
                TEST_RESULT_BUILD_FAILED
                ]

TEST_RESULT_MAPPING = {"success" : TEST_RESULT_OK,
                       "failure" : TEST_RESULT_FAIL,
                       "error" : TEST_RESULT_ERROR,
                       "end" : TEST_RESULT_UNDEF,
                       "ioerr_copy" : TEST_RESULT_IOERR_COPY,
                       "ioerr_disk" : TEST_RESULT_IOERR_DISK,
                       "ioerr_serial" : TEST_RESULT_IOERR_SERIAL,
                       "timeout" : TEST_RESULT_TIMEOUT,
                       "no_image" : TEST_RESULT_NO_IMAGE,
                       "mbed_assert" : TEST_RESULT_MBED_ASSERT,
                       "build_failed" : TEST_RESULT_BUILD_FAILED
                       }


def get_test_result(output):
    """! Parse test 'output' data
    @details If test result not found returns by default TEST_RESULT_TIMEOUT value
    @return Returns found test result
    """
    re_detect = re.compile("\\{(" + "|".join(TEST_RESULT_MAPPING.keys()) + ")\\}")
    for line in "".join(output).splitlines():
        search_result = re_detect.search(line)
        if search_result and search_result.groups():
            return TEST_RESULT_MAPPING[search_result.groups(0)[0]]
    return TEST_RESULT_TIMEOUT


def run_host_test(image_path,
                  disk,
                  port,
                  duration=10,
                  micro=None,
                  reset=None,
                  reset_tout=None,
                  verbose=False,
                  copy_method=None,
                  program_cycle_s=None,
                  digest_source=None,
                  json_test_cfg=None,
                  max_failed_properties=5,
                  enum_host_tests_path=None,
                  run_app=None):
    """! This function runs host test supervisor (executes mbedhtrun) and checks output from host test process.
    @return Tuple with test results, test output and test duration times
    @param image_path Path to binary file for flashing
    @param disk Currently mounted mbed-enabled devices disk (mount point)
    @param port Currently mounted mbed-enabled devices serial port (console)
    @param duration Test case timeout
    @param micro Mbed-nebaled device name
    @param reset Reset type
    @param reset_tout Reset timeout (sec)
    @param verbose Verbose mode flag
    @param copy_method Copy method type (name)
    @param program_cycle_s Wait after flashing delay (sec)
    @param json_test_cfg Additional test configuration file path passed to host tests in JSON format
    @param max_failed_properties After how many unknown properties we will assume test is not ported
    @param enum_host_tests_path Directory where locally defined host tests may reside
    @param run_app Run application mode flag (we run application and grab serial port data)
    @param digest_source if None mbedhtrun will be executed. If 'stdin',
                           stdin will be used via StdInObserver or file (if
                           file name was given as switch option)
    """

    def run_command(cmd):
        """! Runs command and prints proc stdout on screen """
        try:
            p = Popen(cmd,
                    stdout=PIPE,
                    stderr=STDOUT)
        except OSError as e:
            print "mbedgt: run_command(%s) ret= %d failed: %s"% (str(cmd),
                str(e), e.child_traceback)
        return iter(p.stdout.readline, b'')

    if verbose:
        gt_logger.gt_log("selecting test case observer...")
        if digest_source:
            gt_logger.gt_log_tab("selected digest source: %s"% digest_source)

    # Select who will digest test case serial port data
    if digest_source == 'stdin':
        # When we want to scan stdin for test results
        raise NotImplementedError
    elif digest_source is not None:
        # When we want to open file to scan for test results
        raise NotImplementedError

    # Command executing CLI for host test supervisor (in detect-mode)
    cmd = ["mbedhtrun",
            '-d', disk,
            '-p', port,
            '-f', '"%s"'% image_path,
            ]

    # Add extra parameters to host_test
    if program_cycle_s is not None:
        cmd += ["-C", str(program_cycle_s)]
    if copy_method is not None:
        cmd += ["-c", copy_method]
    if micro is not None:
        cmd += ["-m", micro]
    if reset is not None:
        cmd += ["-r", reset]
    if reset_tout is not None:
        cmd += ["-R", str(reset_tout)]
    if json_test_cfg is not None:
        cmd += ["--test-cfg", '"%s"' % str(json_test_cfg)]
    if run_app is not None:
        cmd += ["--run"]    # -f stores binary name!
    if enum_host_tests_path:
        cmd += ["-e", '"%s"'% enum_host_tests_path]

    if verbose:
        gt_logger.gt_log_tab("calling mbedhtrun: %s"% " ".join(cmd))
        gt_logger.gt_log("mbed-host-test-runner: started")

    htrun_output = ''
    start_time = time()

    for line in run_command(cmd):
        htrun_output += line
        sys.stdout.write(line)
        sys.stdout.flush()

    end_time = time()
    testcase_duration = end_time - start_time   # Test case duration from reset to {end}

    result = get_test_result(htrun_output)

    if verbose:
        gt_logger.gt_log("mbed-host-test-runner: stopped")
        gt_logger.gt_log("mbed-host-test-runner: returned '%s'"% result)
    return (result, "".join(htrun_output), testcase_duration, duration)

def run_cli_command(cmd, shell=True, verbose=False):
    """! Runs command from command line
    @param shell Shell command (e.g. ls, ps)
    @param verbose Verbose mode flag
    @return Returns (True, 0) if command was executed successfully else return (False, error code)
    """
    result = True
    ret = 0
    try:
        ret = call(cmd, shell=shell)
        if ret:
            result = False
            if verbose:
                print "mbedgt: [ret=%d] Command: %s"% (int(ret), cmd)
    except OSError as e:
        result = False
        if verbose:
            print "mbedgt: [ret=%d] Command: %s"% (int(ret), cmd)
            print str(e)
            print "mbedgt: traceback..."
            print e.child_traceback
    return (result, ret)

def run_cli_process(cmd):
    """! Runs command as a process and return stdout, stderr and ret code
    @param cmd Command to execute
    @return Tuple of (stdout, stderr, returncode)
    """
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    _stdout, _stderr = p.communicate()
    return _stdout, _stderr, p.returncode
