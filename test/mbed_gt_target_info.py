#!/usr/bin/env python
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
"""

import unittest
from mbed_greentea import mbed_target_info

class CliFunctionality(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_yotta_target_cmd_output(self):
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.0.24"))
        self.assertIn("mbed-gcc", mbed_target_info.parse_yotta_target_cmd_output("mbed-gcc 0.0.14"))

    def test_parse_yotta_search_cmd_output(self):
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_search_cmd_output("frdm-k64f-gcc 0.0.24: Official mbed build target for the mbed frdm-k64f development board."))
        self.assertIn("frdm-k64f-armcc", mbed_target_info.parse_yotta_search_cmd_output("frdm-k64f-armcc 0.0.16: Official mbed build target for the mbed frdm-k64f development board, using the armcc toolchain."))
        self.assertEqual(None, mbed_target_info.parse_yotta_search_cmd_output(""))
        self.assertEqual(None, mbed_target_info.parse_yotta_search_cmd_output("additional results from https://yotta-private.herokuapp.com:"))

if __name__ == '__main__':
    unittest.main()
