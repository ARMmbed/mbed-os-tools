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
import json
from io import StringIO
from mock import patch, mock_open
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
             patch("mbed_lstools.lstools_base.PlatformDatabase.get") as _get,\
             patch('os.listdir') as _listdir:
            _mpr.return_value = True
            _read_htm.return_value = (u'0241BEEFDEAD', {})
            _get.return_value = {
                'platform_name': 'foo_target'
            }
            _listdir.return_value = []
            to_check = self.base.list_mbeds()
            _read_htm.assert_called_once_with('dummy_mount_point')
            _get.assert_called_once_with('0241', device_type='daplink', verbose_data=True)
        self.assertEqual(len(to_check), 1)
        self.assertEqual(to_check[0]['target_id'], "0241BEEFDEAD")
        self.assertEqual(to_check[0]['platform_name'], 'foo_target')

    def test_list_mbeds_invalid_tid(self):
        self.base.return_value = [{'mount_point': 'dummy_mount_point',
                                   'target_id_usb_id': u'0240DEADBEEF',
                                   'serial_port': "dummy_serial_port"},
                                  {'mount_point': 'dummy_mount_point',
                                   'target_id_usb_id': None,
                                   'serial_port': 'not_valid'}]
        with patch("mbed_lstools.lstools_base.MbedLsToolsBase._read_htm_ids") as _read_htm,\
             patch("mbed_lstools.lstools_base.MbedLsToolsBase.mount_point_ready") as _mpr,\
             patch("mbed_lstools.lstools_base.PlatformDatabase.get") as _get,\
             patch('os.listdir') as _listdir:
            _mpr.return_value = True
            _read_htm.side_effect = [(u'0241BEEFDEAD', {}), (None, {})]
            _get.return_value = {
                'platform_name': 'foo_target'
            }
            _listdir.return_value = []
            to_check = self.base.list_mbeds()
            _get.assert_called_once_with('0241', device_type='daplink', verbose_data=True)
        self.assertEqual(len(to_check), 2)
        self.assertEqual(to_check[0]['target_id'], "0241BEEFDEAD")
        self.assertEqual(to_check[0]['platform_name'], 'foo_target')
        self.assertEqual(to_check[1]['target_id'], None)
        self.assertEqual(to_check[1]['platform_name'], None)

    def test_list_mbeds_invalid_platform(self):
        self.base.return_value = [{'mount_point': 'dummy_mount_point',
                                   'target_id_usb_id': u'not_in_target_db',
                                   'serial_port': "dummy_serial_port"}]
        for qos in [FSInteraction.BeforeFilter, FSInteraction.AfterFilter]:
            with patch("mbed_lstools.lstools_base.MbedLsToolsBase._read_htm_ids") as _read_htm,\
                patch("mbed_lstools.lstools_base.MbedLsToolsBase.mount_point_ready") as _mpr,\
                patch("mbed_lstools.lstools_base.PlatformDatabase.get") as _get,\
                patch('os.listdir') as _listdir:
                _mpr.return_value = True
                _read_htm.return_value = (u'not_in_target_db', {})
                _get.return_value = None
                _listdir.return_value = []
                to_check = self.base.list_mbeds()
                _read_htm.assert_called_once_with('dummy_mount_point')
                _get.assert_called_once_with('not_', device_type='daplink', verbose_data=True)
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

    def test_update_device_from_fs_unknown(self):
        device = {}
        self.base._update_device_from_fs(device, False)
        self.assertEqual(device['device_type'], 'unknown')

    def test_detect_device_test(self):
        device_type = self.base._detect_device_type(['Segger.html'])
        self.assertEqual(device_type, 'jlink')

        device_type = self.base._detect_device_type(['MBED.HTM', 'DETAILS.TXT'])
        self.assertEqual(device_type, 'daplink')

    def test_update_device_details_jlink(self):
        jlink_html_contents = ('<html><head><meta http-equiv="refresh" '
                               'content="0; url=http://www.nxp.com/FRDM-KL27Z"/>'
                               '<title>NXP Product Page</title></head><body></body></html>')
        _open = mock_open(read_data=jlink_html_contents)
        dummy_mount_point = 'dummy'
        base_device = {
            'mount_point': dummy_mount_point
        }

        with patch('mbed_lstools.lstools_base.open', _open):
            device = deepcopy(base_device)
            self.base._update_device_details_jlink(device, False, ['Board.html', 'User Guide.html'])
            self.assertEqual(device['url'], 'http://www.nxp.com/FRDM-KL27Z')
            self.assertEqual(device['platform_name'], 'KL27Z')
            _open.assert_called_once_with(os.path.join(dummy_mount_point, 'Board.html'), 'r')

            _open.reset_mock()

            device = deepcopy(base_device)
            self.base._update_device_details_jlink(device, False, ['User Guide.html'])
            self.assertEqual(device['url'], 'http://www.nxp.com/FRDM-KL27Z')
            self.assertEqual(device['platform_name'], 'KL27Z')
            _open.assert_called_once_with(os.path.join(dummy_mount_point, 'User Guide.html'), 'r')

            _open.reset_mock()

            device = deepcopy(base_device)
            self.base._update_device_details_jlink(device, False, ['unhelpful_file.html'])
            self.assertEqual(device, base_device)
            _open.assert_not_called()

    def test_fs_never(self):
        device = {
            'target_id_usb_id': '024075309420ABCE',
            'mount_point': 'invalid_mount_point',
            'serial_port': 'invalid_serial_port'
        }
        with patch("mbed_lstools.lstools_base.MbedLsToolsBase._update_device_from_fs") as _up_fs:
            filter = None
            ret = self.base._fs_never(deepcopy(device), filter, False)
            ret_with_details = self.base._fs_never(deepcopy(device), filter, True)
            self.assertIsNotNone(ret)
            self.assertIsNotNone(ret_with_details)
            self.assertEqual(ret['target_id'], ret['target_id_usb_id'])
            self.assertEqual(ret, ret_with_details)
            _up_fs.assert_not_called()

            filter_in = lambda m: m['platform_name'] == 'K64F'
            ret = self.base._fs_never(deepcopy(device), filter_in, False)
            ret_with_details = self.base._fs_never(deepcopy(device), filter_in, True)
            self.assertIsNotNone(ret)
            self.assertIsNotNone(ret_with_details)
            self.assertEqual(ret, ret_with_details)
            _up_fs.assert_not_called()

            filter_out = lambda m: m['platform_name'] != 'K64F'
            ret = self.base._fs_never(deepcopy(device), filter_out, False)
            ret_with_details = self.base._fs_never(deepcopy(device), filter_out, True)
            self.assertIsNone(ret)
            self.assertEqual(ret, ret_with_details)
            _up_fs.assert_not_called()

    def test_fs_after(self):
        device = {
            'target_id_usb_id': '024075309420ABCE',
            'mount_point': 'invalid_mount_point',
            'serial_port': 'invalid_serial_port'
        }
        with patch("mbed_lstools.lstools_base.MbedLsToolsBase._read_htm_ids") as _read_htm,\
             patch("mbed_lstools.lstools_base.MbedLsToolsBase._details_txt") as _up_details,\
             patch('os.listdir') as _listdir:
            new_device_id = "00017531642046"
            _read_htm.return_value = (new_device_id, {})
            _listdir.return_value = []
            _up_details.return_value = {
                'automation_allowed': '0'
            }
            filter = None
            ret = self.base._fs_after_id_check(deepcopy(device), filter, False)
            _up_details.assert_not_called()
            ret_with_details = self.base._fs_after_id_check(deepcopy(device), filter, True)

            self.assertIsNotNone(ret)
            self.assertIsNotNone(ret_with_details)
            self.assertEqual(ret['target_id'], new_device_id)
            self.assertEqual(ret_with_details['daplink_automation_allowed'], '0')
            self.assertDictContainsSubset(ret, ret_with_details)
            _read_htm.assert_called_with(device['mount_point'])
            _up_details.assert_called_with(device['mount_point'])

            _read_htm.reset_mock()
            _up_details.reset_mock()

            filter_in = lambda m: m['target_id'] == device['target_id_usb_id']
            filter_details = lambda m: m.get('daplink_automation_allowed', None) == '0'

            ret = self.base._fs_after_id_check(deepcopy(device), filter_in, False)
            ret_with_details = self.base._fs_after_id_check(deepcopy(device),
                                                            filter_details,
                                                            True)

            self.assertIsNotNone(ret)
            self.assertIsNone(ret_with_details)
            self.assertEqual(ret['target_id'], new_device_id)
            _read_htm.assert_called_with(device['mount_point'])
            _up_details.assert_not_called()

            _read_htm.reset_mock()
            _up_details.reset_mock()

            filter_out = lambda m: m['target_id'] == new_device_id

            ret = self.base._fs_after_id_check(deepcopy(device), filter_out, False)
            ret_with_details = self.base._fs_after_id_check(deepcopy(device),
                                                            filter_details,
                                                            True)

            self.assertIsNone(ret)
            self.assertIsNone(ret_with_details)
            _read_htm.assert_not_called()
            _up_details.assert_not_called()

    def test_fs_before(self):
        device = {
            'target_id_usb_id': '024075309420ABCE',
            'mount_point': 'invalid_mount_point',
            'serial_port': 'invalid_serial_port'
        }
        with patch("mbed_lstools.lstools_base.MbedLsToolsBase._read_htm_ids") as _read_htm,\
             patch("mbed_lstools.lstools_base.MbedLsToolsBase._details_txt") as _up_details,\
             patch('os.listdir') as _listdir:
            new_device_id = u'00017575430420'
            _read_htm.return_value = (new_device_id, {})
            _listdir.return_value = []
            _up_details.return_value = {
                'automation_allowed': '0'
            }

            filter = None
            ret = self.base._fs_before_id_check(deepcopy(device), filter, False)
            _up_details.assert_not_called()

            ret_with_details = self.base._fs_before_id_check(deepcopy(device), filter, True)
            self.assertIsNotNone(ret)
            self.assertIsNotNone(ret_with_details)
            self.assertEqual(ret['target_id'], new_device_id)
            self.assertEqual(ret_with_details['daplink_automation_allowed'], '0')
            self.assertDictContainsSubset(ret, ret_with_details)
            _read_htm.assert_called_with(device['mount_point'])
            _up_details.assert_called_with(device['mount_point'])

            _read_htm.reset_mock()
            _up_details.reset_mock()

            filter_in = lambda m: m['target_id'] == '00017575430420'
            filter_in_details = lambda m: m['daplink_automation_allowed'] == '0'
            ret = self.base._fs_before_id_check(deepcopy(device), filter_in, False)
            _up_details.assert_not_called()

            ret_with_details = self.base._fs_before_id_check(deepcopy(device),
                                                             filter_in_details,
                                                             True)
            self.assertIsNotNone(ret)
            self.assertIsNotNone(ret_with_details)
            self.assertEqual(ret['target_id'], new_device_id)
            self.assertEqual(ret_with_details['daplink_automation_allowed'], '0')
            self.assertDictContainsSubset(ret, ret_with_details)
            _read_htm.assert_called_with(device['mount_point'])
            _up_details.assert_called_with(device['mount_point'])

            _read_htm.reset_mock()
            _up_details.reset_mock()

            filter_out = lambda m: m['target_id'] == '024075309420ABCE'
            filter_out_details = lambda m: m['daplink_automation_allowed'] == '1'
            ret = self.base._fs_before_id_check(deepcopy(device), filter_out, False)
            _up_details.assert_not_called()

            ret_with_details = self.base._fs_before_id_check(deepcopy(device),
                                                             filter_out_details,
                                                             True)
            self.assertIsNone(ret)
            self.assertIsNone(ret_with_details)
            _read_htm.assert_called_with(device['mount_point'])

class RetargetTestCase(unittest.TestCase):
    """ Test cases that makes use of retargetting
    """

    def setUp(self):
        retarget_data = {
            '0240DEADBEEF': {
                'serial_port' : 'valid'
            }
        }

        _open = mock_open(read_data=json.dumps(retarget_data))

        with patch('os.path.isfile') as _isfile,\
             patch('mbed_lstools.lstools_base.open', _open):
            self.base = DummyLsTools()
            _open.assert_called()

    def tearDown(self):
        pass

    def test_list_mbeds_valid_platform(self):
        self.base.return_value = [{'mount_point': 'dummy_mount_point',
                                   'target_id_usb_id': u'0240DEADBEEF',
                                   'serial_port': None}]
        with patch('mbed_lstools.lstools_base.MbedLsToolsBase._read_htm_ids') as _read_htm,\
             patch('mbed_lstools.lstools_base.MbedLsToolsBase.mount_point_ready') as _mpr,\
             patch('mbed_lstools.lstools_base.PlatformDatabase.get') as _get,\
             patch('os.listdir') as _listdir:
            _mpr.return_value = True
            _read_htm.return_value = (u'0240DEADBEEF', {})
            _get.return_value = {
                'platform_name': 'foo_target'
            }
            _listdir.return_value = []
            to_check = self.base.list_mbeds()
        self.assertEqual(len(to_check), 1)
        self.assertEqual(to_check[0]['serial_port'], 'valid')

if __name__ == '__main__':
    unittest.main()
