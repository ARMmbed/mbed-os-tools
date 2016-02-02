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

import sys
import uuid
from sys import stdout
from mbed_host_tests import BaseHostTest

class EchoTest(BaseHostTest):

    result = None
    COUNT_MAX = 10
    count = 0

    def _callback_end(self, key, value, timestamp):
        pass

    def _callback_exit(self, key, value, timestamp):
        pass

    def _callback_echo(self, key, value, timestamp):
        if self.count < self.COUNT_MAX:
            self.send_kv("echo", uuid.uuid4())
        if key == 'echo':
            self.count += 1
        if self.count == 10:
            self.notify_complete()

    def setup(self):
        self.register_callback("end", self._callback_end)
        self.register_callback("exit", self._callback_exit)
        self.register_callback("echo", self._callback_echo)

        self.send_kv("echo", uuid.uuid4())

    def test(self):
        if self.count >= self.COUNT_MAX:
            self.result = True
        return self.result

    def teardown(self):
        pass
