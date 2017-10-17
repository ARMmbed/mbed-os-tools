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
import re
from mock import patch
from copy import deepcopy

from mbed_lstools.lstools_base import MbedLsToolsBase, FSInteraction

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

    def test_list_mbeds_valid_platform(self):
        self.base.return_value = [{'mount_point': 'dummy_mount_point',
                                   'target_id_usb_id': u'0240DEADBEEF',
                                   'serial_port': "dummy_serial_port"},
                                  {'mount_point': None,
                                   'target_id_usb_id': '00000000000',
                                   'serial_port': 'not_valid'}]
        with patch("mbed_lstools.lstools_base.MbedLsToolsBase._read_htm_ids") as _read_htm,\
             patch("mbed_lstools.lstools_base.MbedLsToolsBase.mount_point_ready") as _mpr,\
             patch("mbed_lstools.lstools_base.PlatformDatabase.get") as _get:
            _mpr.return_value = True
            _read_htm.return_value = (u'0241BEEFDEAD', {})
            _get.return_value = 'foo_target'
            to_check = self.base.list_mbeds()
            _read_htm.assert_called_once_with('dummy_mount_point')
            _get.assert_called_once_with('0241')
        self.assertEqual(len(to_check), 1)
        self.assertEqual(to_check[0]['target_id'], "0241BEEFDEAD")
        self.assertEqual(to_check[0]['platform_name'], 'foo_target')

    def test_list_mbeds_invalid_platform(self):
        self.base.return_value = [{'mount_point': 'dummy_mount_point',
                                   'target_id_usb_id': u'not_in_target_db',
                                   'serial_port': "dummy_serial_port"}]
        for qos in [FSInteraction.BeforeFilter, FSInteraction.AfterFilter]:
            with patch("mbed_lstools.lstools_base.MbedLsToolsBase._read_htm_ids") as _read_htm,\
                patch("mbed_lstools.lstools_base.MbedLsToolsBase.mount_point_ready") as _mpr,\
                patch("mbed_lstools.lstools_base.PlatformDatabase.get") as _get:
                _mpr.return_value = True
                _read_htm.return_value = (u'not_in_target_db', {})
                _get.return_value = None
                to_check = self.base.list_mbeds()
                _read_htm.assert_called_once_with('dummy_mount_point')
                _get.assert_called_once_with('not_')
            self.assertEqual(len(to_check), 1)
            self.assertEqual(to_check[0]['target_id'], "not_in_target_db")
            self.assertEqual(to_check[0]['platform_name'], None)

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

    def test_fs_never(self):
        device = {
            'target_id_usb_id': '024075309420ABCE',
            'mount_point': 'invalid_mount_point',
            'serial_port': 'invalid_serial_port'
        }
        with patch("mbed_lstools.lstools_base.MbedLsToolsBase._update_device_from_htm") as _up_htm:
            filter = re.compile("")
            ret = self.base._fs_never(device, filter)
            self.assertIsNotNone(ret)
            self.assertEqual(ret['target_id'], ret['target_id_usb_id'])
            _up_htm.assert_not_called()

            filter_out = re.compile("NOT-K64F")
            ret = self.base._fs_never(device, filter_out)
            self.assertIsNone(ret)
            _up_htm.assert_not_called()

    def test_fs_after(self):
        device = {
            'target_id_usb_id': '024075309420ABCE',
            'mount_point': 'invalid_mount_point',
            'serial_port': 'invalid_serial_port'
        }
        with patch("mbed_lstools.lstools_base.MbedLsToolsBase._read_htm_ids") as _read_htm:
            new_device_id = "00017531642046"
            _read_htm.return_value = (new_device_id, {})
            filter = re.compile("")
            ret = self.base._fs_after_id_check(device, filter)
            self.assertIsNotNone(ret)
            self.assertEqual(ret['target_id'], new_device_id)
            _read_htm.assert_called_with(device['mount_point'])

            _read_htm.reset_mock()

            filter_out = re.compile("NOT-K64F")
            ret = self.base._fs_after_id_check(device, filter_out)
            self.assertIsNone(ret)
            _read_htm.assert_not_called()

    def test_fs_before(self):
        device = {
            'target_id_usb_id': '024075309420ABCE',
            'mount_point': 'invalid_mount_point',
            'serial_port': 'invalid_serial_port'
        }
        with patch("mbed_lstools.lstools_base.MbedLsToolsBase._read_htm_ids") as _read_htm:
            new_device_id = u'00017575430420'
            _read_htm.return_value = (new_device_id, {})
            filter = re.compile(u'')
            ret = self.base._fs_before_id_check(device, filter)
            self.assertIsNotNone(ret)
            self.assertEqual(ret['target_id'], new_device_id)
            _read_htm.assert_called_with(device['mount_point'])

            _read_htm.reset_mock()

            filter_out = re.compile("NOT-LPC2368")
            ret = self.base._fs_before_id_check(device, filter_out)
            self.assertIsNone(ret)
            _read_htm.assert_called_with(device['mount_point'])

if __name__ == '__main__':
    unittest.main()
