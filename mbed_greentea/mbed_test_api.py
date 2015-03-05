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
from Queue import Queue, Empty
from threading import Thread
from subprocess import call, Popen, PIPE


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

TEST_RESULT_MAPPING = {"success" : TEST_RESULT_OK,
                       "failure" : TEST_RESULT_FAIL,
                       "error" : TEST_RESULT_ERROR,
                       "ioerr_copy" : TEST_RESULT_IOERR_COPY,
                       "ioerr_disk" : TEST_RESULT_IOERR_DISK,
                       "ioerr_serial" : TEST_RESULT_IOERR_SERIAL,
                       "timeout" : TEST_RESULT_TIMEOUT,
                       "no_image" : TEST_RESULT_NO_IMAGE,
                       "end" : TEST_RESULT_UNDEF,
                       "mbed_assert" : TEST_RESULT_MBED_ASSERT
                       }

RE_DETECT_TESTCASE_RESULT = re.compile("\\{(" + "|".join(TEST_RESULT_MAPPING.keys()) + ")\\}")

def run_host_test(image_path, disk, port, duration,
                  micro=None, reset=None, reset_tout=None,
                  verbose=False, copy_method=None, program_cycle_s=None):
    """ This function runs host test supervisor (executes mbedhtrun) and checks
        output from host test process.
    """

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
        result = TEST_RESULT_TIMEOUT
        for line in "".join(output).splitlines():
            search_result = RE_DETECT_TESTCASE_RESULT.search(line)
            if search_result and len(search_result.groups()):
                result = TEST_RESULT_MAPPING[search_result.groups(0)[0]]
                break
        return result

    def get_auto_property_value(property_name, line):
        """ Scans auto detection line from MUT and returns scanned parameter 'property_name'
            Returns string or None if property search failed
        """
        result = None
        if re.search("HOST: Property '%s'"% property_name, line) is not None:
            property = re.search("HOST: Property '%s' = '([\w\d _]+)'"% property_name, line)
            if property is not None and len(property.groups()) == 1:
                result = property.groups()[0]
        return result

    # Command executing CLI for host test supervisor (in detect-mode)
    cmd = ["mbedhtrun",
            '-d', disk,
            '-f', '"%s"'% image_path,
            '-p', port,
            #'-t', str(duration), # This is not used here because timeout is controlled in test suite executing mbedhtrun
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
        print "mbed-host-test-runner: %s"% (" ".join(cmd))

    proc = Popen(cmd, stdout=PIPE)
    obs = ProcessObserver(proc)
    update_once_flag = {}   # Stores flags checking if some auto-parameter was already set
    line = ''
    output = []
    start_time = time()
    while (time() - start_time) < (2 * duration):
        c = get_char_from_queue(obs)
        if c:
            if verbose:
                sys.stdout.write(c)
            c = filter_queue_char(c)
            output.append(c)
            # Give the mbed under test a way to communicate the end of the test
            if c in ['\n', '\r']:

                # Checking for auto-detection information from the test about MUT reset moment
                if 'reset_target' not in update_once_flag and "HOST: Reset target..." in line:
                    # We will update this marker only once to prevent multiple time resets
                    update_once_flag['reset_target'] = True
                    start_time = time()

                # Checking for auto-detection information from the test about timeout
                auto_timeout_val = get_auto_property_value('timeout', line)
                if 'timeout' not in update_once_flag and auto_timeout_val is not None:
                    # We will update this marker only once to prevent multiple time resets
                    update_once_flag['timeout'] = True
                    duration = int(auto_timeout_val)

                # Detect mbed assert:
                if 'mbed assertation failed: ' in line:
                    output.append('{{mbed_assert}}')
                    break

                # Check for test end
                if '{end}' in line:
                    break
                line = ''
            else:
                line += c
    end_time = time()
    testcase_duration = end_time - start_time   # Test case duration from reset to {end}

    c = get_char_from_queue(obs)

    if c:
        if verbose:
            sys.stdout.write(c)
        c = filter_queue_char(c)
        output.append(c)

    # Stop test process
    obs.stop()
    result = get_test_result(output)
    return (result, "".join(output), testcase_duration, duration)

def run_cli_command(cmd, shell=True, verbose=False):
    """ Runs command from command line.
        Return True if command was executed successfully.
    """
    result = True
    try:
        ret = call(cmd, shell=shell)
        if ret:
            result = False
            if verbose:
                print "mbed-ls: [ret=%d] Command: %s"% (int(ret), cmd)
    except Exception as e:
        result = False
        if verbose:
            print "mbed-ls: [ret=%d] Command: %s"% (int(ret), cmd)
            print str(e)
    return result
