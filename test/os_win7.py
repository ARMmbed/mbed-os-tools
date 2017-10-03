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
                 b'_??_USBSTOR#Disk&Ven_MBED&Prod_microcontroller&Rev_1.0#8&bcddc05&0&0672FF485550755187045151&0#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}'),
                (b'\\DosDevices\\D:',
                 b'_??_USBSTOR#Disk&Ven_SEGGER&Prod_MSD_Volume&Rev_1.00#8&1b8e102b&0&000440035522&0#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}')],
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
            return value_dict[key][index]
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
