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
from mock import patch

from mbed_lstools.lstools_base import MbedLsToolsBase

class DummyLsTools(MbedLsToolsBase):
    return_value = []
    def find_candidates(self):
        return self.return_value

try:
    basestring
except NameError:
    # Python 3
    basestring = str

class BasicTestCase(unittest.TestCase):
    """ Basic test cases checking trivial asserts
    """

    def setUp(self):
        self.base = DummyLsTools()

    def tearDown(self):
        pass

    def test_list_mbeds(self):
        self.base.return_value = [{'mount_point': 'dummy_mount_point',
                                   'target_id_usb_id': '0240DEADBEEF',
                                   'serial_port': "dummy_serial_port"},
                                  {'mount_point': None,
                                   'target_id_usb_id': '00000000000',
                                   'serial_port': 'not_valid'}]
        with patch("mbed_lstools.lstools_base.MbedLsToolsBase._read_htm_target_id") as _read_htm,\
             patch("mbed_lstools.lstools_base.PlatformDatabase.get") as _get:
            _read_htm.return_value = b"0241BEEFDEAD"
            _get.return_value = 'foo_target'
            to_check = self.base.list_mbeds()
            _read_htm.assert_called_once_with('dummy_mount_point')
            _get.assert_called_once_with('0241')
        self.assertEqual(len(to_check), 1)
        self.assertEqual(to_check[0]['target_id'], "0241BEEFDEAD")
        self.assertEqual(to_check[0]['platform_name'], 'foo_target')

    def test_list_manufacture_ids(self):
        table_str = self.base.list_manufacture_ids()
        self.assertTrue(isinstance(table_str, basestring))

    def test_mock_manufacture_ids_default_multiple(self):
        # oper='+'
        for mid, platform_name in [('0341', 'TEST_PLATFORM_NAME_1'),
                                   ('0342', 'TEST_PLATFORM_NAME_2'),
                                   ('0343', 'TEST_PLATFORM_NAME_3')]:
            self.base.mock_manufacture_id(mid, platform_name)
            self.assertEqual(platform_name, self.base.plat_db.get(mid))

    def test_mock_manufacture_ids_minus(self):
        # oper='+'
        for mid, platform_name in [('0341', 'TEST_PLATFORM_NAME_1'),
                                   ('0342', 'TEST_PLATFORM_NAME_2'),
                                   ('0343', 'TEST_PLATFORM_NAME_3')]:
            self.base.mock_manufacture_id(mid, platform_name)
            self.assertEqual(platform_name, self.base.plat_db.get(mid))

        # oper='-'
        mock_ids = self.base.mock_manufacture_id('0342', '', oper='-')
        self.assertEqual('TEST_PLATFORM_NAME_1', self.base.plat_db.get("0341"))
        self.assertEqual(None, self.base.plat_db.get("0342"))
        self.assertEqual('TEST_PLATFORM_NAME_3', self.base.plat_db.get("0343"))

    def test_mock_manufacture_ids_star(self):
        # oper='+'
        for mid, platform_name in [('0341', 'TEST_PLATFORM_NAME_1'),
                                   ('0342', 'TEST_PLATFORM_NAME_2'),
                                   ('0343', 'TEST_PLATFORM_NAME_3')]:
            self.base.mock_manufacture_id(mid, platform_name)

            self.assertEqual(platform_name, self.base.plat_db.get(mid))

        # oper='-'
        self.base.mock_manufacture_id('*', '', oper='-')
        self.assertEqual(None, self.base.plat_db.get("0341"))
        self.assertEqual(None, self.base.plat_db.get("0342"))
        self.assertEqual(None, self.base.plat_db.get("0343"))

if __name__ == '__main__':
    unittest.main()
