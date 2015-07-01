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

# Check if 'serial' module is installed
# TODO: check in sys.modules if pySerial is installed
import re
from sys import stdout

from threading import Lock
from threading import Thread
from mbed_host_tests.host_tests_runner.mbed_base import Mbed


class HostTestResults:
    """ Test results set by host tests
    """
    def __init__(self):
        self.RESULT_SUCCESS = 'success'
        self.RESULT_FAILURE = 'failure'
        self.RESULT_ERROR = 'error'
        self.RESULT_IO_SERIAL = 'ioerr_serial'
        self.RESULT_NO_IMAGE = 'no_image'
        self.RESULT_IOERR_COPY = "ioerr_copy"
        self.RESULT_PASSIVE = "passive"
        self.RESULT_NOT_DETECTED = "not_detected"
        self.RESULT_MBED_ASSERT = "mbed_assert"


class Test(HostTestResults):
    """ Base class for host test's test runner
    """
    def __init__(self, options=None):
        """ ctor
        """
        self.mbed = Mbed(options)
        self.mutex = Lock() # Used to sync console output prints
        self.print_thread = None
        self.print_thread_flag = False  # True, serial dump, False - serial dump stop (thread ends)

    def detect_test_config(self, verbose=False):
        """! Detects test case configuration

        @param verbose Verbose mode on/off

        @return Function returns dictionary of read during handshake properties and its values

        @details This code is detecting extra prints on console sent by test case
                 running on hardware (on on other end of communication channel.
                 In mbed case it is a serial port).
        """
        result = {}
        while True:
            line = self.mbed.serial_readline()
            if "{start}" in line:
                self.notify("HOST: Start test...")
                break
            elif line.startswith('+'):
                # This is probably preamble with test case warning
                self.notify(line.strip())
            else:
                # Detect if this is property from TEST_ENV print
                m = re.search('{([\w_]+);(.+)}}', line, flags=re.DOTALL)
                if m and len(m.groups()) == 2:
                    key = m.group(1)

                    # clean up quote characters and concatinate
                    # multiple quoted strings.
                    g = re.findall('[\"\'](.*?)[\"\']',m.group(2))
                    if len(g)>0:
                        val = "".join(g)
                    else:
                        val = m.group(2)

                    # This is most likely auto-detection property
                    result[key] = val
                    if verbose:
                        self.notify("HOST: Property '%s' = '%s'"% (key, val))
                else:
                    # We can check if this is TArget Id in mbed specific format
                    m2 = re.search('^([\$]+)([a-fA-F0-9]+)', line[:-1])
                    if m2 and len(m2.groups()) == 2:
                        if verbose:
                            target_id = m2.group(1) + m2.group(2)
                            self.notify("HOST: TargetID '%s'"% target_id)
                            self.notify(line[len(target_id):-1])
                    else:
                        self.notify("HOST: Unknown property: %s"% line.strip())
        return result

    def run(self):
        """ Test runner for host test. This function will start executing
            test and forward test result via serial port to test suite
        """
        pass

    def setup(self):
        """! Setup and check if configuration for test is correct.

        @details This function can for example check if serial port is already opened
        """
        result = True
        if not self.mbed.serial:
            result = False
            self.print_result(self.RESULT_IO_SERIAL)
        return result

    def notify(self, message, newline=True):
        """! On screen notification function

        @param message Text message sent to stdout directly
        @param newline If True we will send NewLine at the end of message

        @details This function is mutex protected
        """
        if message is not None:
            self.mutex.acquire(1)
            try:
                if newline:
                    print message
                else:
                    stdout.write(message)
                stdout.flush()
            except:
                pass
            self.mutex.release()

    def dump_serial(self):
        """! Function is used to print serial port data

        Used in background allows developers to continue with host test execution
        and at the same time print serial port data.

        @details This function will create separate thread.
                 To stop dumping serial call dump_serial_end() method
        """
        if not self.print_thread_flag:
            if self.print_thread is None:
                self.print_thread_flag = True
                self.print_thread = Thread(target=self.dump_serial_thread_func)
                self.print_thread.start()
                return True
        return False

    def dump_serial_thread_func(self):
        """! This is thread worker function used to dump serial port on console

        @details This function is called in dump_serial() function
        """
        self.notify('HOST: Serial port dump started...')
        while self.print_thread_flag:
            c = self.mbed.serial_read(512)
            if c is not None:
                self.notify(c, newline=False)
            else:
                self.print_result(selftest.RESULT_IO_SERIAL)
        self.print_thread = None

    def dump_serial_end(self):
        """! Stop dumping serial port in background

        @details Set 'print_thread_flag' flag to False to stop serial port dump thread
        """
        self.print_thread_flag = False

    def print_result(self, result):
        """! Test result unified printing function

        @param result Should be a member of HostTestResults.RESULT_* enums
        """
        self.notify("\r\n{{%s}}\r\n{{end}}" % result)

    def finish(self):
        """ dctor for this class, finishes tasks and closes resources
        """
        self.dump_serial_end()
        # We are waiting for serial port thread dump to end
        while self.print_thread_flag:
            pass

class DefaultTestSelectorBase(Test):
    """! Test class with serial port initialization

    @details This is a base for other test selectors, initializes
    """
    def __init__(self, options=None):
        HostTestResults.__init__(self)
        Test.__init__(self, options=options)
