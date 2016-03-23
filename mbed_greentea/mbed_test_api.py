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
from mbed_greentea.mbed_coverage_api import coverage_dump_file
from mbed_greentea.mbed_coverage_api import coverage_pack_hex_payload


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
    re_detect = re.compile(r"\{result;([\w+_]*)\}")

    for line in output.split():
        search_result = re_detect.search(line)
        if search_result:
            if search_result.group(1) in TEST_RESULT_MAPPING:
                return TEST_RESULT_MAPPING[search_result.group(1)]
            else:
                return TEST_RESULT_UNDEF
    return TEST_RESULT_TIMEOUT


def run_host_test(image_path,
                  disk,
                  port,
                  yotta_target,
                  target_id,
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
    @return Tuple with test results, test output, test duration times and test case results
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
        return p

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
    if target_id is not None:
        cmd += ["-t", target_id]
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

    p = run_command(cmd)
    for line in iter(p.stdout.readline, b''):
        htrun_output += line
        # When dumping output to file both \r and \n will be a new line
        # To avoid this "extra new-line" we only use \n at the end
        if verbose:
            sys.stdout.write(line.rstrip() + '\n')
            sys.stdout.flush()
    
    # Check if process was terminated by signal
    returncode = p.wait()
    if returncode < 0:
        return returncode

    end_time = time()
    testcase_duration = end_time - start_time   # Test case duration from reset to {end}

    result = get_test_result(htrun_output)
    result_test_cases = get_testcase_result(htrun_output)
    test_cases_summary = get_testcase_summary(htrun_output)
    get_coverage_data(yotta_target, htrun_output)

    if verbose:
        gt_logger.gt_log("mbed-host-test-runner: stopped")
        gt_logger.gt_log("mbed-host-test-runner: returned '%s'"% result)
    return (result, htrun_output, testcase_duration, duration, result_test_cases, test_cases_summary)

def get_testcase_utest(output, test_case_name):
    """ Example test case prints
    [1455553765.52][CONN][RXD] >>> Running case #1: 'Simple Test'...
    [1455553765.52][CONN][RXD] {{__testcase_start;Simple Test}}
    [1455553765.52][CONN][INF] found KV pair in stream: {{__testcase_start;Simple Test}}, queued...
    [1455553765.58][CONN][RXD] Simple test called
    [1455553765.58][CONN][RXD] {{__testcase_finish;Simple Test;1;0}}
    [1455553765.58][CONN][INF] found KV pair in stream: {{__testcase_finish;Simple Test;1;0}}, queued...
    [1455553765.70][CONN][RXD] >>> 'Simple Test': 1 passed, 0 failed
    """

    # Return string with all non-alphanumerics backslashed;
    # this is useful if you want to match an arbitrary literal
    # string that may have regular expression metacharacters in it.
    escaped_test_case_name = re.escape(test_case_name)

    re_tc_utest_log_start  = re.compile(r"^\[(\d+\.\d+)\]\[(\w+)\]\[(\w+)\] >>> Running case #(\d)+: '(%s)'"% escaped_test_case_name)
    re_tc_utest_log_finish = re.compile(r"^\[(\d+\.\d+)\]\[(\w+)\]\[(\w+)\] >>> '(%s)': (\d+) passed, (\d+) failed"% escaped_test_case_name)

    tc_log_lines = []
    for line in output.splitlines():

        # utest test case start string search
        m = re_tc_utest_log_start.search(line)
        if m:
            tc_log_lines.append(line)
            continue

        # If utest test case end string found
        m = re_tc_utest_log_finish.search(line)
        if m:
            tc_log_lines.append(line)
            break

        # Continue adding utest log lines
        if tc_log_lines:
            tc_log_lines.append(line)

    return tc_log_lines

def get_coverage_data(yotta_target, output):
    # Example GCOV output
    # [1456840876.73][CONN][RXD] {{__coverage_start;c:\Work\core-util/source/PoolAllocator.cpp.gcda;6164636772393034c2733f32...a33e...b9}}
    gt_logger.gt_log("checking for GCOV data...")
    re_gcov = re.compile(r"^\[(\d+\.\d+)\][^\{]+\{\{(__coverage_start);([^;]+);([^}]+)\}\}$")
    for line in output.splitlines():
        m = re_gcov.search(line)
        if m:
            timestamp, _, gcov_path, gcov_payload = m.groups()
            try:
                bin_gcov_payload = coverage_pack_hex_payload(gcov_payload)
                coverage_dump_file(yotta_target, gcov_path, bin_gcov_payload)
            except Exception as e:
                gt_logger.gt_log_err("error while handling GCOV data: " + str(e))
            gt_logger.gt_log_tab("storing %d bytes in '%s'"% (len(bin_gcov_payload), gcov_path))

def get_testcase_summary(output):
    re_tc_summary = re.compile(r"^\[(\d+\.\d+)\][^\{]+\{\{(__testcase_summary);(\d+);(\d+)\}\}")
    for line in output.splitlines():
        m = re_tc_summary.search(line)
        if m:
            timestamp, _, passes, failures = m.groups()
            return int(passes), int(failures)
    return None

def get_testcase_result(output):
    result_test_cases = {}  # Test cases results
    re_tc_start = re.compile(r"^\[(\d+\.\d+)\][^\{]+\{\{(__testcase_start);([^;]+)\}\}")
    re_tc_finish = re.compile(r"^\[(\d+\.\d+)\][^\{]+\{\{(__testcase_finish);([^;]+);(\d+);(\d+)\}\}")

    for line in output.splitlines():
        m = re_tc_start.search(line)
        if m:
            timestamp, _, testcase_id = m.groups()
            if testcase_id not in result_test_cases:
                result_test_cases[testcase_id] = {}

            # Data collected when __testcase_start is fetched
            result_test_cases[testcase_id]['time_start'] = float(timestamp)
            result_test_cases[testcase_id]['utest_log'] = get_testcase_utest(output, testcase_id)

            # Data collected when __testcase_finish is fetched
            result_test_cases[testcase_id]['duration'] = 0.0
            result_test_cases[testcase_id]['result_text'] = 'ERROR'
            result_test_cases[testcase_id]['time_end'] = float(timestamp)
            result_test_cases[testcase_id]['passed'] = 0
            result_test_cases[testcase_id]['failed'] = 0
            result_test_cases[testcase_id]['result'] = -4096
            continue

        m = re_tc_finish.search(line)
        if m:
            timestamp, _, testcase_id, testcase_passed, testcase_failed = m.groups()

            testcase_passed = int(testcase_passed)
            testcase_failed = int(testcase_failed)

            testcase_result = 0 # OK case
            if testcase_failed != 0:
                testcase_result = testcase_failed   # testcase_result > 0 is FAILure

            if testcase_id not in result_test_cases:
                result_test_cases[testcase_id] = {}
            # Setting some info about test case itself
            result_test_cases[testcase_id]['duration'] = 0.0
            result_test_cases[testcase_id]['result_text'] = 'OK'
            result_test_cases[testcase_id]['time_end'] = float(timestamp)
            result_test_cases[testcase_id]['passed'] = testcase_passed
            result_test_cases[testcase_id]['failed'] = testcase_failed
            result_test_cases[testcase_id]['result'] = testcase_result
            # Assign human readable test case result
            if testcase_result > 0:
                result_test_cases[testcase_id]['result_text'] = 'FAIL'
            elif testcase_result < 0:
                result_test_cases[testcase_id]['result_text'] = 'ERROR'

            if 'time_start' in result_test_cases[testcase_id]:
                result_test_cases[testcase_id]['duration'] = result_test_cases[testcase_id]['time_end'] - result_test_cases[testcase_id]['time_start']
            else:
                result_test_cases[testcase_id]['duration'] = 0.0

    return result_test_cases

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
