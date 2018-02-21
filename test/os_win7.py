#!/usr/bin/env python
# coding: utf-8
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
import sys
import os
from mock import MagicMock, patch, call

# Mock the winreg and _winreg module for non-windows python
_winreg = MagicMock()
sys.modules['_winreg']  = _winreg
sys.modules['winreg'] = _winreg

from mbed_lstools.windows import MbedLsToolsWin7

class Win7TestCase(unittest.TestCase):
    """ Basic test cases checking trivial asserts
    """

    def setUp(self):
        self.lstool = MbedLsToolsWin7()
        _winreg.HKEY_LOCAL_MACHINE = None
        _winreg.OpenKey.side_effect = None
        _winreg.EnumValue.side_effect = None
        _winreg.EnumKey.side_effect = None
        _winreg.QueryValue.side_effect = None
        _winreg.QueryInfoKey.side_effect = None
        _winreg.CreateKey.reset_mock()
        _winreg.CreateKeyEx.reset_mock()
        _winreg.DeleteKey.reset_mock()
        _winreg.DeleteKeyEx.reset_mock()
        _winreg.DeleteValue.reset_mock()
        _winreg.SetValue.reset_mock()
        _winreg.SetValueEx.reset_mock()
        _winreg.SaveKey.reset_mock()

    def test_os_supported(self):
        pass

    def test_empty_reg(self):
        value_dict = {
            (None, 'SYSTEM\\MountedDevices'): [
                ('\\DosDevices\\F:',
                 u'_??_USBSTOR#Disk&Ven_MBED&Prod_VFS&Rev_0.1#0240000032044e4500367009997b00086781000097969900&0#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}'.encode('utf-16le')),
                ('\\DosDevices\\D:',
                 u'_??_USBSTOR#Disk&Ven_SEGGER&Prod_MSD_Volume&Rev_1.00#8&1b8e102b&0&000440035522&0#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}'.encode('utf-16le'))],
            ((None, 'SYSTEM\\CurrentControlSet'), 'Services\\usbccgp\\Enum'): [
                ('Count', 0),
                ('NextInstance', 0)
            ]
        }
        key_dict = {
            (None, 'SYSTEM\\CurrentControlSet'): ['Services\\usbccgp\\Enum'],
            (None, 'SYSTEM\\CurrentControlSet'): ['Enum\\USB'],
            ((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'):
            ['ROOT_HUB30', 'VID_0416&PID_511E', 'VID_0416&PID_511E&MI_00',
             'VID_8087&PID_0A2B', 'Vid_80EE&Pid_CAFE']
        }
        self.setUpRegistry(value_dict, key_dict)
        candidates = self.lstool.find_candidates()
        self.assertEqual(_winreg.OpenKey.mock_calls, [
            call(_winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet'),
            call((_winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'),
            call((_winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet'), 'Services\\usbccgp\\Enum'),
            call((_winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet'), 'Services\\mbedComposite\\Enum')
        ])
        self.assertEqual(candidates, [])

    def assertNoRegMut(self):
        """Assert that the registry was not mutated in this test"""
        _winreg.CreateKey.assert_not_called()
        _winreg.CreateKeyEx.assert_not_called()
        _winreg.DeleteKey.assert_not_called()
        _winreg.DeleteKeyEx.assert_not_called()
        _winreg.DeleteValue.assert_not_called()
        _winreg.SetValue.assert_not_called()
        _winreg.SetValueEx.assert_not_called()
        _winreg.SaveKey.assert_not_called()

    def setUpRegistry(self, value_dict, key_dict):
        all_keys = set(value_dict.keys()) | set(key_dict.keys())
        def open_key_effect(key, subkey):
            if ((key, subkey) in all_keys or key in all_keys):
                return key, subkey
            else:
                raise OSError((key, subkey))
        _winreg.OpenKey.side_effect = open_key_effect
        def enum_value(key, index):
            try:
                a, b = value_dict[key][index]
                return a, b, None
            except KeyError:
                raise OSError
        _winreg.EnumValue.side_effect = enum_value
        def enum_key(key, index):
            try:
                return key_dict[key][index]
            except KeyError:
                raise OSError
        _winreg.EnumKey.side_effect = enum_key
        def query_value(key, subkey):
            try:
                return value_dict[(key, subkey)]
            except KeyError:
                raise OSError
        _winreg.QueryValueEx.side_effect = query_value
        def query_info_key(key):
            return (len(key_dict.get(key, [])),
                    len(value_dict.get(key, [])))
        _winreg.QueryInfoKey.side_effect = query_info_key

    def test_one_dev(self):
        value_dict = {
            (None, 'SYSTEM\\MountedDevices'): [
                ('\\DosDevices\\C:', u'NOT A VALID MBED DRIVE'.encode('utf-16le')),
                ('\\DosDevices\\F:',
                 u'_??_USBSTOR#Disk&Ven_MBED&Prod_VFS&Rev_0.1#11010000442031204c364141303031313431303397969903&0#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}'.encode('utf-16le'))
            ],
            ((None, 'SYSTEM\\CurrentControlSet'), 'Services\\usbccgp\\Enum'): [
                ('0', 'USB\\VID_5986&PID_0706\\5&31ac2c0b&0&8'),
                ('Count', 2),
                ('NextInstance', 2)
            ],
            ((None, 'SYSTEM\\CurrentControlSet'), 'Services\\mbedComposite\\Enum'): [
                ('0', 'USB\\VID_0D28&PID_0204\\11010000442031204c364141303031313431303397969903'),
                ('Count', 1),
                ('NextInstance', 1)
            ],
            ((((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'), 'VID_5986&PID_0706\\5&31ac2c0b&0&8'), 'ParentIdPrefix'): ('6&3beba67&0', None),
            ((((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'), 'VID_5986&PID_0706&MI_00\\6&3beba67&0&0000'),
                'Service'): ('SPUVCbv', None),
            (((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'),
                'VID_0D28&PID_0204\\11010000442031204c364141303031313431303397969903'): [],
            ((((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'),
                'VID_0D28&PID_0204&MI_00\\11010000442031204c364141303031313431303397969903'),
                'Service'): ('USBSTOR', None),
            ((((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'),
                'VID_0D28&PID_0204&MI_01\\11010000442031204c364141303031313431303397969903'),
                'Device Parameters'): [('PortName', 'COM7')],
            (((((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'),
                'VID_0D28&PID_0204&MI_01\\11010000442031204c364141303031313431303397969903'),
                'Device Parameters'), 'PortName'): ('COM7', None),
            ((((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'),
                'VID_0D28&PID_0204&MI_03\\11010000442031204c364141303031313431303397969903'),
                'Service'): ('HidUsb', None)
        }
        key_dict = {
            (None, 'SYSTEM\\CurrentControlSet'): ['Services\\usbccgp\\Enum', 'Services\\mbedComposite\\Enum'],
            (None, 'SYSTEM\\CurrentControlSet'): ['Enum\\USB'],
            ((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'):
            ['ROOT_HUB30', 'VID_0416&PID_511E', 'VID_0416&PID_511E&MI_00',
             'VID_0416&PID_511E&MI_01', 'VID_046D&PID_C03D',
             'VID_046D&PID_C313', 'VID_046D&PID_C313&MI_00',
             'VID_046D&PID_C313&MI_01', 'VID_046D&PID_C52B',
             'VID_046D&PID_C52B&MI_00', 'VID_046D&PID_C52B&MI_01',
             'VID_046D&PID_C52B&MI_02', 'VID_0483&PID_374B',
             'VID_0483&PID_374B&MI_00', 'VID_0483&PID_374B&MI_01',
             'VID_0483&PID_374B&MI_02', 'VID_0930&PID_6545',
             'VID_0D28&PID_0204', 'VID_0D28&PID_0204&MI_00',
             'VID_0D28&PID_0204&MI_01', 'VID_0D28&PID_0204&MI_03',
             'VID_1366&PID_1015', 'VID_1366&PID_1015&MI_00',
             'VID_1366&PID_1015&MI_02', 'VID_1366&PID_1015&MI_03',
             'VID_138A&PID_0090', 'VID_17EF&PID_100F', 'VID_17EF&PID_1010',
             'VID_17EF&PID_6019', 'VID_18D1&PID_4EE1', 'VID_195D&PID_2047',
             'VID_195D&PID_2047&MI_00', 'VID_195D&PID_2047&MI_01',
             'VID_195D&PID_2047&MI_02', 'VID_1A40&PID_0101', 'VID_1FD2&PID_5003',
             'VID_1FD2&PID_5003&MI_00', 'VID_1FD2&PID_5003&MI_01',
             'VID_413C&PID_2107', 'VID_5986&PID_0706', 'VID_5986&PID_0706&MI_00',
             'VID_8087&PID_0A2B', 'Vid_80EE&Pid_CAFE'],
            (((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'),
                'VID_5986&PID_0706&MI_00'): ['6&3beba67&0&0000'],
            (((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'),
                'VID_0D28&PID_0204&MI_00'): ['11010000442031204c364141303031313431303397969903'],
            (((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'),
                'VID_0D28&PID_0204&MI_01'): ['11010000442031204c364141303031313431303397969903'],
            ((((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'),
                'VID_0D28&PID_0204&MI_01'), '11010000442031204c364141303031313431303397969903'): ['Device Parameters'],
            (((None, 'SYSTEM\\CurrentControlSet'), 'Enum\\USB'),
                'VID_0D28&PID_0204&MI_03'): ['11010000442031204c364141303031313431303397969903']
        }
        self.setUpRegistry(value_dict, key_dict)

        with patch('mbed_lstools.windows.MbedLsToolsWin7._run_cli_process') as _cliproc:
            _cliproc.return_value = ("", "", 0)
            expected_info = {
                'mount_point': u'F:',
                'serial_port': 'COM7',
                'target_id_usb_id': u'11010000442031204c364141303031313431303397969903'
            }

            devices = self.lstool.find_candidates()
            self.assertIn(expected_info, devices)
            self.assertNoRegMut()

    def test_mount_point_ready(self):
        with patch('mbed_lstools.windows.MbedLsToolsWin7._run_cli_process') as _cliproc:
            _cliproc.return_value = ("dummy", "", 0)
            self.assertTrue(self.lstool.mount_point_ready("dummy"))

            _cliproc.reset_mock()

            _cliproc.return_value = ("", "dummy", 1)
            self.assertFalse(self.lstool.mount_point_ready("dummy"))


if __name__ == '__main__':
    unittest.main()
