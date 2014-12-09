"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

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

import os
import sys
import platform

from lmtools_win7 import LmToolsWin7
from lmtools_ubuntu import LmToolsUbuntu

"""
Example usage:

lmtools = lmtools_factory()
lmtools.load_mbed_description('targets.json')
lm = lmtools.list_mbeds()

for mbed in lm:
    print mbed['serial_port']
"""


def lmtools_factory():
    """ Factory producing lmtools depending on OS it is working on
    """
    result = None
    os_info = lmtools_os_info()
    if (os_info[0] == 'nt' and os_info[1] == 'Windows'):
        result = LmToolsWin7()
    elif (os_info[0] == 'posix' and os_info[1] == 'Linux' and ('Ubuntu' in os_info[3])):
        result = LmToolsUbuntu()
    return result

def lmtools_os_info():
    """ Returns information about running OS
    """
    result = (os.name,
              platform.system(),
              platform.release(),
              platform.version(),
              sys.platform)
    return result
