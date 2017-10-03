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
import sys
from mock import MagicMock

# Mock the winreg and _winreg module for non-windows python
_winreg = MagicMock()
sys.modules['_winreg']  = _winreg
sys.modules['winreg'] = _winreg


from mbed_lstools.lstools_win7 import MbedLsToolsWin7


class Win7TestCase(unittest.TestCase):
    """ Basic test cases checking trivial asserts
    """

    def setUp(self):
        self.lstool = MbedLsToolsWin7()

    def test_os_supported(self):
        pass

    def test_empty_reg(self):
        _winreg.QueryInfoKey.return_value = (0, 0)
        self.lstool.find_candidates()
        _winreg.OpenKey.assert_called_with(_winreg.HKEY_LOCAL_MACHINE,
                                           'SYSTEM\MountedDevices')
        _winreg.QueryInfoKey.assert_called_with(_winreg.OpenKey.return_value)
        pass

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

    def test_one_nucleo_dev(self):
        _winreg.HKEY_LOCAL_MACHINE = None
        value_dict = {
            (None, 'SYSTEM\MountedDevices'): [
                (b'\\DosDevices\\F:',
                 b'_\x00?\x00?\x00_\x00U\x00S\x00B\x00S\x00T\x00O\x00R\x00#\x00D\x00i\x00s\x00k\x00&\x00V\x00e\x00n\x00_\x00M\x00B\x00E\x00D\x00&\x00P\x00r\x00o\x00d\x00_\x00V\x00F\x00S\x00&\x00R\x00e\x00v\x00_\x000\x00.\x001\x00#\x000\x002\x004\x000\x000\x000\x000\x000\x003\x002\x000\x004\x004\x00e\x004\x005\x000\x000\x003\x006\x007\x000\x000\x009\x009\x009\x007\x00b\x000\x000\x000\x008\x006\x007\x008\x001\x000\x000\x000\x000\x009\x007\x009\x006\x009\x009\x000\x000\x00&\x000\x00#\x00{\x005\x003\x00f\x005\x006\x003\x000\x007\x00-\x00b\x006\x00b\x00f\x00-\x001\x001\x00d\x000\x00-\x009\x004\x00f\x002\x00-\x000\x000\x00a\x000\x00c\x009\x001\x00e\x00f\x00b\x008\x00b\x00}\x00'),
                (b'\\DosDevices\\D:',
                 b'_\x00?\x00?\x00_\x00U\x00S\x00B\x00S\x00T\x00O\x00R\x00#\x00D\x00i\x00s\x00k\x00&\x00V\x00e\x00n\x00_\x00S\x00E\x00G\x00G\x00E\x00R\x00&\x00P\x00r\x00\x00o\x00d\x00_\x00M\x00S\x00D\x00_\x00V\x00o\x00l\x00u\x00m\x00e\x00&\x00R\x00e\x00v\x00_\x001\x00.\x000\x000#\x008\x00&\x001\x00b\x008\x00e\x001\x000\x002\x00b\x00&\x000\x00&\x000\x000\x000\x004\x004\x000\x000\x003\x005\x005\x002\x002\x00&\x000\x00#\x00{\x005\x003\x00f\x005\x006\x003\x000\x007\x00-\x00b\x006\x00b\x00f\x00-\x001\x001\x00d\x000\x00-\x009\x004\x00f\x002\x00-\x000\x000\x00a\x000\x00c\x009\x001\x00e\x00f\x00b\x008\x00b\x00}\x00')],
            ((((((None, 'SYSTEM\CurrentControlSet\Enum'), 'USB'),
                'VID_0416&PID_511E'), '000440035522'), 'Device Parameters'), 'PortName'): ('COM7', None)
        }
        key_dict = {
            ((((None, 'SYSTEM\CurrentControlSet\Enum'), 'USB'), 'VID_0416&PID_511E'), '000440035522'): ['Device Parameters', 'Properties'],
            ((None, 'SYSTEM\CurrentControlSet\Enum'), 'USB'):
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
             'VID_8087&PID_0A2B', 'Vid_80EE&Pid_CAFE']
        }
        def open_key_effect(key, subkey):
            return key, subkey
        _winreg.OpenKey.side_effect = open_key_effect
        def enum_value(key, index):
            a, b = value_dict[key][index]
            return a, b, None
        _winreg.EnumValue.side_effect = enum_value
        def enum_key(key, index):
            return key_dict[key][index]
        _winreg.EnumKey.side_effect = enum_key
        def query_value(key, subkey):
            return value_dict[(key, subkey)]
        _winreg.QueryValueEx.side_effect = query_value
        def query_info_key(key):
            return (len(key_dict.get(key, [])),
                    len(value_dict.get(key, [])))
        _winreg.QueryInfoKey.side_effect = query_info_key
        devices = self.lstool.find_candidates()
        print(devices)
        self.assertNoRegMut()


if __name__ == '__main__':
    unittest.main()
