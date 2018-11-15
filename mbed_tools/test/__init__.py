"""
mbed SDK
Copyright (c) 2011-2016 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""


"""! @package mbed-host-tests

Flash, reset and  perform host supervised tests on mbed platforms.
Write your own programs (import this package) or use 'mbedhtrun' command line tool instead.

"""

from mbed_tools.test import host_tests_plugins
from mbed_tools.test.host_tests_registry import HostRegistry
from mbed_tools.test.host_tests import BaseHostTest, event_callback

from mbed_tools.test.mbed_greentea_cli import main

# Set the default baud rate
DEFAULT_BAUD_RATE = 9600

###############################################################################
# Functional interface for test supervisor registry
###############################################################################


def get_plugin_caps(methods=None):
    if not methods:
        methods = ['CopyMethod', 'ResetMethod']
    result = {}
    for method in methods:
        result[method] = host_tests_plugins.get_plugin_caps(method)
    return result

