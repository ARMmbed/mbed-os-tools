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

from mbed_host_tests import is_host_test
from mbed_host_tests import get_host_test

class BasicHostTestsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basic_get_host_test(self):
        self.assertNotEqual(None, get_host_test('default'))
        self.assertNotEqual(None, get_host_test('default_auto'))
        
    def test_basic_is_host_test(self):
        self.assertEqual(False, is_host_test(''))
        self.assertEqual(False, is_host_test(None))

        self.assertEqual(True, is_host_test('default'))
        self.assertEqual(True, is_host_test('default_auto'))


if __name__ == '__main__':
    unittest.main()
