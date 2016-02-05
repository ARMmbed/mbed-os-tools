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
"""

from time import time


class BaseHostTestAbstract(object):
    """ Base class for each host-test test cases with standard
        setup, test and teardown set of functions
    """

    name = ''   # name of the host test (used for local registration)
    event_queue = None      # To main even loop
    dut_event_queue = None  # To DUT

    def __notify_prn(self, text, nl=True):
        if self.event_queue:
            if nl:
                text += '\n'
            self.event_queue.put(('__notify_prn', text, time()))

    def __notify_conn_lost(self, text):
        if self.event_queue:
            self.event_queue.put(('__notify_conn_lost', text, time()))

    def __notify_dut(self, key, value):
        """! Send data over serial to DUT """
        if self.event_queue:
            self.dut_event_queue.put((key, value, time()))

    def notify_complete(self, result=None):
        """! Notify main even loop that host test finished processing
        @param result True for success, False failure. If None - no action in main even loop
        """
        if self.event_queue:
            self.event_queue.put(('__notify_complete', result, time()))

    def notify_conn_lost(self, text):
        """! Notify main even loop that there was a DUT-host test connection error
        @param consume If True htrun will process (consume) all remaining events
        """
        self.__notify_conn_lost(text)

    def log(self, text):
        """! Send log message to main event loop """
        self.__notify_prn(text)

    def send_kv(self, key, value):
        """! Send Key-Value data to DUT """
        self.__notify_dut(key, value)

    def setup(self):
        """! Setup your tests and callbacks """
        raise NotImplementedError

    def result(self):
        """! Returns host test result (True, False or None) """
        raise NotImplementedError

    def teardown(self):
        """! Blocking always guaranteed test teardown """
        raise NotImplementedError


class HostTestCallbackBase(BaseHostTestAbstract):

    def __init__(self):
        BaseHostTestAbstract.__init__(self)
        self.__callbacks = {}
        self.__restricted_callbacks = [
            '__coverage_start',
            '__testcase_start',
            '__testcase_finish',
            '__exit',
        ]

        self.__printable = [
            '__coverage_start',
            '__testcase_start',
            '__testcase_finish'
        ]

        self.__assign_default_callbacks()

    def __callback_default(self, key, value, timestamp):
        """! Default callback """
        #self.log("CALLBACK: key=%s, value=%s, timestamp=%f"% (key, value, timestamp))
        pass

    def __assign_default_callbacks(self):
        """! Assigns default callback handlers """
        for key in self.__printable:
            self.__callbacks[key] = self.__callback_default

    def register_callback(self, key, callback):
        """! Register callback for a specific event (key: event name) """

        # Non-string keys are not allowed
        if type(key) is not str:
            raise TypeError

        # Event starting with '__' are reserved
        if key.startswith('__'):
            raise ValueError

        # We predefined few callbacks you can't use
        if key in self.__restricted_callbacks:
            raise ValueError

        # And finally callback should be callable
        if not callable(callback):
            raise TypeError

        self.__callbacks[key] = callback

    def get_callbacks(self):
        return self.__callbacks

    def setup(self):
        pass

    def result(self):
        pass

    def teardown(self):
        pass


class BaseHostTest(HostTestCallbackBase):

    def __init__(self):
        HostTestCallbackBase.__init__(self)

    def setup(self):
        pass

    def result(self):
        pass

    def teardown(self):
        pass
