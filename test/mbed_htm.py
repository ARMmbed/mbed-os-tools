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
import os
import errno
import logging

from mbed_lstools.main import create


test_mbed_htm_k64f_url = '<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code=02400203D94B0E7724B7F3CF"/>'
test_mbed_htm_l152re_url = '<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code=07100200656A9A955A0F0CB8"/>'
test_mbed_htm_lpc1768_url = '<meta http-equiv="refresh" content="0; url=http://mbed.org/start?auth=101000000000000000000002F7F1869557200730298d254d3ff3509e3fe4722d&loader=11972&firmware=16457&configuration=4" />'


class ParseMbedHTMTestCase(unittest.TestCase):
    """ Unit tests checking HTML parsing code for 'mbed.htm' files
    """

    def setUp(self):
        self.mbeds = create()

    def tearDown(self):
        pass

    def test_mbed_htm_k64f_url(self):
        target_id = self.mbeds.scan_html_line_for_target_id(test_mbed_htm_k64f_url)
        self.assertEqual('02400203D94B0E7724B7F3CF', target_id)

    def test_mbed_htm_l152re_url(self):
        target_id = self.mbeds.scan_html_line_for_target_id(test_mbed_htm_l152re_url)
        self.assertEqual('07100200656A9A955A0F0CB8', target_id)

    def test_mbed_htm_lpc1768_url(self):
        target_id = self.mbeds.scan_html_line_for_target_id(test_mbed_htm_lpc1768_url)
        self.assertEqual('101000000000000000000002F7F1869557200730298d254d3ff3509e3fe4722d', target_id)

    def test_(self):
        pass

if __name__ == '__main__':
    unittest.main()
