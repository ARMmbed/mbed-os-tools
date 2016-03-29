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
from mbed_greentea import mbed_coverage_api


class GreenteaCoverageAPI(unittest.TestCase):

    def setUp(self):
        pass

    def test_x(self):
        pass

    def test_coverage_pack_hex_payload(self):
        # This function takesstring as input
        r = mbed_coverage_api.coverage_pack_hex_payload('')
        self.assertEqual(bytearray(b''), r)

        r = mbed_coverage_api.coverage_pack_hex_payload('6164636772')
        self.assertEqual(bytearray(b'adcgr'), r)

        r = mbed_coverage_api.coverage_pack_hex_payload('.')    # '.' -> 0x00
        self.assertEqual(bytearray(b'\x00'), r)

        r = mbed_coverage_api.coverage_pack_hex_payload('...')    # '.' -> 0x00
        self.assertEqual(bytearray(b'\x00\x00\x00'), r)

        r = mbed_coverage_api.coverage_pack_hex_payload('.6164636772.')    # '.' -> 0x00
        self.assertEqual(bytearray(b'\x00adcgr\x00'), r)


if __name__ == '__main__':
    unittest.main()
