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


from mbed_host_tests import BaseHostTest


class DefaultAuto(BaseHostTest):
    """ Simple, basic host test's test runner waiting for serial port
        output from MUT, no supervision over test running in MUT is executed.
    """

    result = None

    def _callback_end(self, key, value, timeout):
        if value == 'success':
            self.result = True
        elif value == 'failure':
            self.result = False

    def _callback_exit(self, key, value, timeout):
        self.notify_complete()

    def setup(self):
        self.register_callback('end', self._callback_end)
        self.register_callback('exit', self._callback_exit)

    def test(self):
        return self.result

    def teardown(self):
        pass
