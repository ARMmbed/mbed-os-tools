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
from mbed_lstools.lstools_win7 import MbedLsToolsWin7

# Since we don't have mock, let's monkey-patch

def get_mbed_devices_new(self):
    return [
        ('\\DosDevices\\D:', '_??_USBSTOR#Disk&Ven_MBED&Prod_XPRO&Rev_1.00#9&35913356&0&ATML2127031800007973&0#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}'),
    ]

class Win7TestCase(unittest.TestCase):
    """ Basic test cases checking trivial asserts
    """

    def setUp(self):
        pass

    def test_os_supported(self):
        pass
        
    def test_get_mbeds(self):
        
        m = MbedLsToolsWin7()
        
        func_type = type(MbedLsToolsWin7.get_mbed_devices)
        m.get_mbed_devices = func_type(get_mbed_devices_new, m, MbedLsToolsWin7)

        mbeds = m.get_mbeds()
        
        self.assertIsNotNone(mbeds)
        self.assertEqual(1, len(mbeds))
        
        mbed = mbeds[0]
        
        self.assertEqual("D:", mbed[0])
        self.assertEqual("ATML2127031800007973", mbed[1])
        


if __name__ == '__main__':
    unittest.main()
