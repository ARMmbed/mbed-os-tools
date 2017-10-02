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

if __name__ == '__main__':
    unittest.main()
