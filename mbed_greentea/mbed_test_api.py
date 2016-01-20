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
from time import time, sleep
from Queue import Queue, Empty
from threading import Thread
from subprocess import call, Popen, PIPE

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

RE_DETECT_TESTCASE_RESULT = re.compile("\\{(" + "|".join(TEST_RESULT_MAPPING.keys()) + ")\\}")

def get_test_result(output):
    """! Parse test 'output' data
    @details If test result not found returns by default TEST_RESULT_TIMEOUT value
    @return Returns found test result
    """
    result = TEST_RESULT_TIMEOUT
    for line in "".join(output).splitlines():
        search_result = RE_DETECT_TESTCASE_RESULT.search(line)
        if search_result and search_result.groups():
            result = TEST_RESULT_MAPPING[search_result.groups(0)[0]]
            break
    return result


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

    class StdInObserver(Thread):
        """ Process used to read stdin only as console input from MUT
        """
        def __init__(self):
            Thread.__init__(self)
            self.queue = Queue()
            self.daemon = True
            self.active = True
            self.start()

        def run(self):
            while self.active:
                c = sys.stdin.read(1)
                self.queue.put(c)

        def stop(self):
            self.active = False

    class FileObserver(Thread):
        """ process used to read file content as console input from MUT
        """
        def __init__(self, filename):
            Thread.__init__(self)
            self.filename = filename
            self.queue = Queue()
            self.daemon = True
            self.active = True
            self.start()

        def run(self):
            with open(self.filename) as f:
                while self.active:
                    c = f.read(1)
                    self.queue.put(c)

        def stop(self):
            self.active = False

    class ProcessObserver(Thread):
        """ Default process used to observe stdout of another process as console input from MUT
        """
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

            # Try stopping mbed-host-test
            try:
                self.proc.stdin.close()
            finally:
                pass

            # Give 5 sec for mbedhtrun to exit
            ret_code = None
            for i in range(5):
                ret_code = self.proc.poll()
                # A None value indicates that the process hasn't terminated yet.
                if ret_code is not None:
                    break
                sleep(1)

            if ret_code is None:            # Kill it
                print 'Terminating mbed-host-test(mbedhtrun) process (PID %s)' % self.proc.pid
                try:
                    self.proc.terminate()
                except Exception as e:
                    print "ProcessObserver.stop(): %s" % str(e)

    def get_char_from_queue(obs):
        """ Get character from queue safe way
        """
        try:
            c = obs.queue.get(block=True, timeout=0.5)
            # signals to queue job is done
            obs.queue.task_done()
        except Empty:
            c = None
        except:
            raise
        return c

    def filter_queue_char(c):
        """ Filters out non ASCII characters from serial port
        """
        if ord(c) not in range(128):
            c = ' '
        return c

    def get_auto_property_value(property_name, line):
        """! Scans auto detection line from MUT and returns scanned parameter 'property_name'
        @details Host test case has to print additional properties for test to be set up
        @return Returns string or None if property search failed
        """
        result = None
        if re.search("HOST: Property '%s'"% property_name, line) is not None:
            property = re.search("HOST: Property '%s' = '([\w\d _]+)'"% property_name, line)
            if property is not None and len(property.groups()) == 1:
                result = property.groups()[0]
        return result

    # Detect from where input should be taken, if no --digest switch is specified
    # normal test execution can be performed

    if verbose:
        gt_logger.gt_log("selecting test case observer...")
        if digest_source:
            gt_logger.gt_log_tab("selected digest source: %s"% digest_source)

    # Select who will digest test case serial port data
    if digest_source == 'stdin':
        # When we want to scan stdin for test results
        obs = StdInObserver()
    elif digest_source is not None:
        # When we want to open file to scan for test results
        obs = FileObserver(digest_source)
    else:
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
        proc = Popen(cmd, stdin=PIPE, stdout=PIPE)
        obs = ProcessObserver(proc)

    result = None
    update_once_flag = {}   # Stores flags checking if some auto-parameter was already set
    unknown_property_count = 0
    total_duration = 20     # This for flashing, reset and other serial port operations
    line = ''
    output = []
    start_time = time()
    while (time() - start_time) < (total_duration):
        try:
            c = get_char_from_queue(obs)
        except Exception as e:
            output.append('get_char_from_queue(obs): %s'% str(e))
            break
        if c:
            if verbose:
                sys.stdout.write(c)
            c = filter_queue_char(c)
            output.append(c)
            # Give the mbed under test a way to communicate the end of the test
            if c in ['\n', '\r']:

                # Check for unknown property prints
                # If there are too many we will stop test execution and assume test is not ported
                if "HOST: Unknown property" in line:
                    unknown_property_count += 1
                    if unknown_property_count >= max_failed_properties:
                        output.append('{{error}}')
                        break

                # Checking for auto-detection information from the test about MUT reset moment
                if 'reset_target' not in update_once_flag and "HOST: Reset target..." in line:
                    # We will update this marker only once to prevent multiple time resets
                    update_once_flag['reset_target'] = True
                    start_time = time()
                    total_duration = duration   # After reset we gonna use real test case duration

                # Checking for auto-detection information from the test about timeout
                auto_timeout_val = get_auto_property_value('timeout', line)
                if 'timeout' not in update_once_flag and auto_timeout_val is not None:
                    # We will update this marker only once to prevent multiple time resets
                    update_once_flag['timeout'] = True
                    total_duration = int(auto_timeout_val)

                # Detect mbed assert:
                if 'mbed assertation failed: ' in line:
                    output.append('{{mbed_assert}}')
                    break

                # Check for test end. Only a '{{end}}' in the start of line indicates a test end.
                # A sub string '{{end}}' may also appear in an error message.
                if re.search('^\{\{end\}\}', line, re.I):
                    break
                line = ''
            else:
                line += c
    else:
        result = TEST_RESULT_TIMEOUT

    if not '{end}' in line:
        output.append('{{end}}')

    c = get_char_from_queue(obs)

    if c:
        if verbose:
            sys.stdout.write(c)
        c = filter_queue_char(c)
        output.append(c)

    # Stop test process
    obs.stop()

    end_time = time()
    testcase_duration = end_time - start_time   # Test case duration from reset to {end}

    if verbose:
        gt_logger.gt_log("mbed-host-test-runner: stopped")
    if not result:
        result = get_test_result(output)
    if verbose:
        gt_logger.gt_log("mbed-host-test-runner: returned '%s'"% result)
    return (result, "".join(output), testcase_duration, duration)

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
    except Exception as e:
        result = False
        if verbose:
            print "mbedgt: [ret=%d] Command: %s"% (int(ret), cmd)
            print str(e)
    return (result, ret)

def run_cli_process(cmd):
    """! Runs command as a process and return stdout, stderr and ret code
    @param cmd Command to execute
    @return Tuple of (stdout, stderr, returncode)
    """
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    _stdout, _stderr = p.communicate()
    return _stdout, _stderr, p.returncode
