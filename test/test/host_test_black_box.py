#!/usr/bin/env python
# Copyright (c) 2018, Arm Limited and affiliates.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import os
import re

import threading
from builtins import super
from mbed_os_tools.test import init_host_test_cli_params
from mbed_os_tools.test.host_tests_runner.host_test_default  import DefaultTestSelector
from mock import patch, MagicMock
from pyfakefs import fake_filesystem_unittest


class MockThread(threading.Thread):
    def __init__(self, target=None, args=None):
        super().__init__(target=target, args=args)
        print('Mock Thread constr')
        self._terminates = 0
        self.exitcode = 0 # TODO maybe this needs to be setable? Mock sys.exit

    def terminate(self):
        self._terminates += 1

class MockSerial(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        self._open = True
        self._rx_counter = 0
        self._tx_buffer = ""
        self._rx_buffer = ""
        self._upstream_write_cb = None

    def read(self, count):
        contents = self._rx_buffer[self._rx_counter:count]
        self._rx_counter += len(contents)
        return contents

    def write(self, data):
        self._tx_buffer += data
        if self._upstream_write_cb:
            # TODO this may not work...
            self._upstream_write_cb(data)

    def close(self):
        self._open = False

    def downstream_write(self, data):
        self._rx_buffer += data

    def on_upstream_write(self, func):
        self._upstream_write_cb = func

kv_regex = re.compile(r"\{\{([\w\d_-]+);([^\}]+)\}\}")

class MockMbedDevice(object):
    def __init__(self, serial):
        self._synced = False
        self._kvs = []
        self._serial = serial
        self._serial.on_upstream_write(self.on_write)

    def handle_kv(self, key, value):
        if not self._synced:
            if key == "__sync":
                self._synced = True
                self.send_kv(key, value)
                self.on_sync()
        else:
            pass

    def send_kv(self, key, value):
        self._serial.downstream_write("{{{{{};{}}}}}\r\n".format(key, value))

    def on_write(self, data):
        kvs = kv_regex.findall(data)

        for key, value in kvs:
            self.handle_kv(key, value)
            self._kvs.append((key, value))

    def on_sync(self):
        self._serial.downstream_write(
            "{{__timeout;15}}\r\n"
            "{{__host_test_name;default_auto}}\r\n"
            "{{end;success}}\n"
            "{{__exit;0}}\r\n"
        )


def _process_side_effect(target=None, args=None):
    return MockThread(target=target, args=args)

class BlackBoxHostTestTestCase(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def tearDown(self):
        pass

    def test_host_test_has_setup_teardown_attribute(self):
        platform_info = {
            "platform_name": "K64F",
            "target_id": "0240000031754e45000c0018948500156461000097969900",
            "mount_point": os.path.normpath("/mnt/DAPLINK"),
            "serial_port": os.path.normpath("/dev/ttyACM0"),
        }
        image_path = os.path.normpath(
            "BUILD/tests/K64F/GCC_ARM/TESTS/network/interface/interface.bin"
        )
        self.fs.create_file(image_path)
        self.fs.create_dir(platform_info['mount_point'])
        args = (
            'mbedhtrun -m {} -p {}:9600 -f '
            '"{}" -e "TESTS/host_tests" -d {} -c default '
            '-t {} -r default '
            '-C 4 --sync 5 -P 60'
        ).format(
            platform_info['platform_name'],
            platform_info['serial_port'],
            image_path,
            platform_info['mount_point'],
            platform_info['target_id']
        ).split()

        with patch('sys.argv', new=args) as _argv,\
             patch('os.name', new='posix'),\
             patch('os.uname', return_value=('Linux',), create=True),\
             patch('mbed_os_tools.detect.create') as _detect,\
             patch('mbed_os_tools.test.host_tests_plugins.host_test_plugins.call') as _call,\
             patch('mbed_os_tools.test.host_tests_runner.host_test_default.Process') as _process,\
             patch('mbed_os_tools.test.host_tests_conn_proxy.conn_primitive_serial.Serial') as _serial:
            _process.side_effect = _process_side_effect
            _detect.return_value.list_mbeds.return_value = [
                platform_info
            ]
            _call.return_value = 0

            mock_serial = MockSerial()
            mock_device = MockMbedDevice(mock_serial)
            _serial.return_value = mock_serial

            test_selector = DefaultTestSelector(init_host_test_cli_params())
            result = test_selector.execute()
            test_selector.finish()

            matched_calls = [
                ca for ca in _call.call_args_list if ca[0][0][0] == "cp"
            ]
            cmd_args = matched_calls[0][0][0]
            self.assertEqual(cmd_args[1], image_path)
            self.assertTrue(cmd_args[2].startswith(platform_info["mount_point"]))
            self.assertTrue(cmd_args[2].endswith(os.path.splitext(image_path)[1]))

            self.assertEqual(result, 0)

if __name__ == '__main__':
    unittest.main()
