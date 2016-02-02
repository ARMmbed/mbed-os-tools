"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

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

    def _notify_prn(self, text, nl=True):
        if self.event_queue:
            if nl:
                text += '\n'
            self.event_queue.put(('__notify_prn', text, time()))

    def notify_complete(self, consume=True):
        """! Notify htrun that host test finished processing
        @param consume If True htrun will process (consume) all remaining events
        """
        if self.event_queue:
            self.event_queue.put(('__notify_complete', consume, time()))

    def log(self, text):
        self._notify_prn(text)

    def _notify_dut(self, key, value):
        """! Send data over serial to DUT """
        if self.event_queue:
            self.dut_event_queue.put((key, value, time()))

    def send_kv(self, key, value):
        self._notify_dut(key, value)

    def setup(self):
        pass

    def test(self):
        pass

    def teardown(self):
        pass


class HostTestCallbackBase(BaseHostTestAbstract):

    def __init__(self):
        BaseHostTestAbstract.__init__(self)
        self.callbacks = {}
        self._restricted_callbacks = ['coverage_start',
            'testcase_start',
            'testcase_finish'
            ]

        self.printable = ['coverage_start',
            'testcase_start',
            'testcase_finish'
            ]

        self._assign_callbacks()

    def _callback_default(self, key, value, timestamp):
        """! Default callback """
        self.log("CALLBACK: key=%s, value=%s, timestamp=%f"% (key, value, timestamp))

    def _callback_forward(self, key, value, timestamp):
        """! We want to print on stdout things Greentea can capture"""
        # TODO:
        pass

    def _assign_callbacks(self):
        """! Assigns default callback handlers
        """
        for key in self.printable:
            self.callbacks[key] = self._callback_forward

    def register_callback(self, key, callback):
        if type(key) is not str:
            raise TypeError

        if key in self._restricted_callbacks:
            raise ValueError

        if not callable(callback):
            raise TypeError

        self.callbacks[key] = callback

    def setup(self):
        pass

    def test(self):
        pass

    def teardown(self):
        pass


class BaseHostTest(HostTestCallbackBase):

    def __init__(self):
        HostTestCallbackBase.__init__(self)

    def setup(self):
        pass

    def test(self):
        pass

    def teardown(self):
        pass
