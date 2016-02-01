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

import re
from sys import stdout
from time import time

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
    def __init__(self, options):
        """ ctor
        """
        self.mbed = Mbed(options)
        self.mutex = Lock() # Used to sync console output prints
        self.print_thread = None
        self.print_thread_flag = False  # True, serial dump, False - serial dump stop (thread ends)

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

    def print_result(self, result):
        """! Test result unified printing function

        @param result Should be a member of HostTestResults.RESULT_* enums
        """
        self.notify("\r\n{{%s}}\r\n{{end}}" % result)

    def finish(self):
        """ dctor for this class, finishes tasks and closes resources
        """
        pass


class DefaultTestSelectorBase(Test):
    """! Test class with serial port initialization

    @details This is a base for other test selectors, initializes
    """
    def __init__(self, options):
        HostTestResults.__init__(self)
        Test.__init__(self, options=options)
