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


import uuid
from mbed_host_tests import BaseHostTest

class EchoTest(BaseHostTest):

    __result = None
    COUNT_MAX = 10
    count = 0
    uuid_sent = []
    uuid_recv = []

    def __send_echo_uuid(self):
        str_uuid = str(uuid.uuid4())
        self.send_kv("echo", str_uuid)
        self.uuid_sent.append(str_uuid)

    def _callback_echo(self, key, value, timestamp):
        self.uuid_recv.append(value)
        if key == 'echo':
            self.count += 1
        if self.count == self.COUNT_MAX:
            self.notify_complete(False)
        else:
            self.__send_echo_uuid()

    def setup(self):
        self.register_callback("echo", self._callback_echo)

        self.__send_echo_uuid()  # Echo no. 1

    def result(self):
        self.__result = self.uuid_sent == self.uuid_recv
        return self.__result

    def teardown(self):
        pass
