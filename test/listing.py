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
import sys
import errno
import logging

from mbed_lstools.main import create


class MbedListingestCase(unittest.TestCase):
    """ UNit tests for mbed-ls ability to list connected devices
    """

    def setUp(self):
        self.mbeds = create()

    def tearDown(self):
        pass

    def test_porting_create(self):
        self.assertNotEqual(None, self.mbeds)

    def test_list_mbeds_ret_type(self):
        self.assertNotEqual(None, self.mbeds.list_mbeds())
        self.assertIs(type(self.mbeds.list_mbeds()), list)

    def test_list_mbeds_ext_ret_type(self):
        self.assertNotEqual(None, self.mbeds.list_mbeds_ext())
        self.assertIs(type(self.mbeds.list_mbeds_ext()), list)

    def test_manufacture_ids_format(self):
        for dev in self.mbeds.plat_db.all_ids():
            self.assertEqual(len(dev), 4)

    def test_list_mbeds_mandatory_fields_exist(self):
        mbeds = self.mbeds.list_mbeds()
        for mbed in mbeds:
            self.assertIn('platform_name', mbed)
            self.assertIn('target_id', mbed)
            self.assertIn('mount_point', mbed)
            self.assertIn('serial_port', mbed)
            self.assertIn('target_id_mbed_htm', mbed)
            self.assertIn('target_id_usb_id', mbed)

    def test_list_mbeds_ext_mandatory_fields_exist(self):
        mbeds = self.mbeds.list_mbeds_ext()
        for mbed in mbeds:
            self.assertIn('platform_name_unique', mbed)
            self.assertIn('daplink_version', mbed)

    def test_list_platforms(self):
        platforms = self.mbeds.list_platforms()
        self.assertIs(type(platforms), list)
        for p in platforms:
            self.assertIs(type(p), str)

    def test_list_platforms_ext(self):
        platforms = self.mbeds.list_platforms_ext()
        self.assertIs(type(platforms), dict)
        for p in platforms:
            self.assertIs(type(p), str)
            self.assertIs(type(platforms[p]), int)
            self.assertTrue(platforms[p] >= 0)

    def test_get_dummy_platform(self):
        p = self.mbeds.get_dummy_platform('K64F')
        self.assertIs(type(p), dict)

        self.assertIn('platform_name', p)
        self.assertIn('platform_name_unique', p)
        self.assertIn('target_id', p)
        self.assertIn('mount_point', p)
        self.assertIn('serial_port', p)
        self.assertIn('target_id_mbed_htm', p)
        self.assertIn('target_id_usb_id', p)
        self.assertIn('daplink_version', p)

if __name__ == '__main__':
    unittest.main()
