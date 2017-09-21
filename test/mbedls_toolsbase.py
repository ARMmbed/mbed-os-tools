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

from mbed_lstools.lstools_base import MbedLsToolsBase

try:
    basestring
except NameError:
    # Python 3
    basestring = str

class BasicTestCase(unittest.TestCase):
    """ Basic test cases checking trivial asserts
    """

    def setUp(self):
        self.base = MbedLsToolsBase()

    def tearDown(self):
        pass

    def test_example(self):
        self.assertEqual(True, True)
        self.assertNotEqual(True, False)

    def test_list_manufacture_ids(self):
        table_str = self.base.list_manufacture_ids()
        self.assertTrue(isinstance(table_str, basestring))

    def test_mock_read(self):
        mock_data = self.base.mock_read()

        self.assertIs(type(mock_data), dict)

    def test_mock_read_write(self):
        mock_data = self.base.mock_read()
        self.assertIs(type(mock_data), dict)

        ret = self.base.mock_write(mock_data)
        self.assertTrue(ret)

        mock_data_after_write = self.base.mock_read()
        self.assertIs(type(mock_data_after_write), dict)

        self.assertEqual(mock_data, mock_data_after_write)

    def test_mock_read_write_custom_data(self):
        """
        1. Read original mock data
        2. Write custom data
        3. Read (custom) mock data
        4. Write original mock data
        """

        mock_data = self.base.mock_read()
        self.assertIs(type(mock_data), dict)

        custom_mock_data = {
            "0240": "K__F",
            "ABCD": "SOME_PLATFORM"
        }

        ret = self.base.mock_write(custom_mock_data)
        self.assertTrue(ret)

        mock_data_after_write = self.base.mock_read()
        self.assertIs(type(mock_data_after_write), dict)

        self.assertEqual(custom_mock_data, mock_data_after_write)

        ret = self.base.mock_write(mock_data)
        self.assertTrue(ret)

        mock_data_after_write = self.base.mock_read()
        self.assertIs(type(mock_data_after_write), dict)

        self.assertEqual(mock_data, mock_data_after_write)

    def test_mock_manufacture_ids_default(self):
        mock_data = self.base.mock_read()
        self.assertIs(type(mock_data), dict)

        # oper='+'
        mock_ids = self.base.mock_manufacture_ids('TEST', 'TEST_PLATFORM_NAME')

        self.assertIn('TEST', mock_ids)
        self.assertEqual('TEST_PLATFORM_NAME', mock_ids['TEST'])

        ret = self.base.mock_write(mock_data)
        self.assertTrue(ret)

    def test_mock_manufacture_ids_default_multiple(self):
        mock_data = self.base.mock_read()
        self.assertIs(type(mock_data), dict)

        # oper='+'
        for mid, platform_name in [('TEST_1', 'TEST_PLATFORM_NAME_1'),
                                   ('TEST_2', 'TEST_PLATFORM_NAME_2'),
                                   ('TEST_3', 'TEST_PLATFORM_NAME_3')]:
            mock_ids = self.base.mock_manufacture_ids(mid, platform_name)

            self.assertIn(mid, mock_ids)
            self.assertEqual(platform_name, mock_ids[mid])

        ret = self.base.mock_write(mock_data)
        self.assertTrue(ret)

    def test_mock_manufacture_ids_minus(self):
        mock_data = self.base.mock_read()
        self.assertIs(type(mock_data), dict)

        # oper='+'
        for mid, platform_name in [('TEST_1', 'TEST_PLATFORM_NAME_1'),
                                   ('TEST_2', 'TEST_PLATFORM_NAME_2'),
                                   ('TEST_3', 'TEST_PLATFORM_NAME_3')]:
            mock_ids = self.base.mock_manufacture_ids(mid, platform_name)

            self.assertIn(mid, mock_ids)
            self.assertEqual(platform_name, mock_ids[mid])

        # oper='-'
        mock_ids = self.base.mock_manufacture_ids('TEST_2', '', oper='-')
        self.assertIn('TEST_1', mock_ids)
        self.assertNotIn('TEST_2', mock_ids)
        self.assertIn('TEST_3', mock_ids)

        ret = self.base.mock_write(mock_data)
        self.assertTrue(ret)

    def test_mock_manufacture_ids_star(self):
        mock_data = self.base.mock_read()
        self.assertIs(type(mock_data), dict)

        # oper='+'
        for mid, platform_name in [('TEST_1', 'TEST_PLATFORM_NAME_1'),
                                   ('TEST_2', 'TEST_PLATFORM_NAME_2'),
                                   ('TEST_3', 'TEST_PLATFORM_NAME_3')]:
            mock_ids = self.base.mock_manufacture_ids(mid, platform_name)

            self.assertIn(mid, mock_ids)
            self.assertEqual(platform_name, mock_ids[mid])

        # oper='-'
        mock_ids = self.base.mock_manufacture_ids('*', '', oper='-')
        self.assertNotIn('TEST_1', mock_ids)
        self.assertNotIn('TEST_2', mock_ids)
        self.assertNotIn('TEST_3', mock_ids)
        self.assertFalse(mock_ids)

        ret = self.base.mock_write(mock_data)
        self.assertTrue(ret)

if __name__ == '__main__':
    unittest.main()
