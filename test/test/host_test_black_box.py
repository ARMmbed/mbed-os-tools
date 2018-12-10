#!/usr/bin/env python
# Copyright (c) 2018, Arm Limited and affiliates.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import os
import re
from builtins import super
from copy import copy
from mbed_os_tools.test import init_host_test_cli_params
from mbed_os_tools.test.host_tests_runner.host_test_default  import DefaultTestSelector
from mock import patch, MagicMock

from .mocks.environment.linux import MockTestEnvironmentLinux
from .mocks.environment.darwin import MockTestEnvironmentDarwin
from .mocks.environment.windows import MockTestEnvironmentWindows

mock_platform_info = {
    "platform_name": "K64F",
    "target_id": "0240000031754e45000c0018948500156461000097969900",
    "mount_point": os.path.normpath("mnt/DAPLINK"),
    "serial_port": os.path.normpath("dev/ttyACM0"),
}
mock_image_path = os.path.normpath(
    "BUILD/tests/K64F/GCC_ARM/TESTS/network/interface/interface.bin"
)

class BlackBoxHostTestTestCase(unittest.TestCase):

    def test_host_test_linux(self):
        with MockTestEnvironmentLinux(self, mock_platform_info, mock_image_path) as _env:
            test_selector = DefaultTestSelector(init_host_test_cli_params())
            result = test_selector.execute()
            test_selector.finish()

        self.assertEqual(result, 0)

    def test_host_test_darwin(self):
        with MockTestEnvironmentDarwin(self, mock_platform_info, mock_image_path) as _env:
            test_selector = DefaultTestSelector(init_host_test_cli_params())
            result = test_selector.execute()
            test_selector.finish()

        self.assertEqual(result, 0)

    def test_host_test_windows(self):
        win_mock_platform_info = copy(mock_platform_info)
        win_mock_platform_info["mount_point"] = "D:"
        win_mock_platform_info["serial_port"] = "COM5"
        with MockTestEnvironmentWindows(self, mock_platform_info, mock_image_path) as _env:
            test_selector = DefaultTestSelector(init_host_test_cli_params())
            result = test_selector.execute()
            test_selector.finish()

        self.assertEqual(result, 0)

if __name__ == '__main__':
    unittest.main()
