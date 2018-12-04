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

class MockTestEnvironment(object):

    def __init__(self, test_case, platform_info, image_path):
        self._test_case = test_case
        self._platform_info = platform_info
        self._image_path = image_path
        self._patch_definitions = []
        self.patches = {}

        args = (
            'mbedhtrun -m {} -p {}:9600 -f '
            '"{}" -e "TESTS/host_tests" -d {} -c default '
            '-t {} -r default '
            '-C 4 --sync 5 -P 60'
        ).format(
            self._platform_info['platform_name'],
            self._platform_info['serial_port'],
            self._image_path,
            self._platform_info['mount_point'],
            self._platform_info['target_id']
        ).split()
        self.patch('sys.argv', new=args)

        # Mock detect
        detect_mock = MagicMock()
        detect_mock.return_value.list_mbeds.return_value = [
            self._platform_info
        ]
        self.patch('mbed_os_tools.detect.create', new=detect_mock)

        # Mock process
        self.patch(
            'mbed_os_tools.test.host_tests_runner.host_test_default.Process',
            new=MagicMock(side_effect=_process_side_effect)
        )
        self.patch(
            'mbed_os_tools.test.host_tests_plugins.host_test_plugins.call',
            new=MagicMock(return_value=0)
        )

        # Mock serial
        mock_serial = MockSerial()
        mock_device = MockMbedDevice(mock_serial)
        self.patch(
            'mbed_os_tools.test.host_tests_conn_proxy.conn_primitive_serial.Serial',
            new=MagicMock(return_value=mock_serial)
        )


    def patch(self, path, **kwargs):
        self._patch_definitions.append((path, patch(path, **kwargs)))

    def __enter__(self):
        self._test_case.fs.create_file(self._image_path)
        self._test_case.fs.create_dir(self._platform_info['mount_point'])

        for path, patcher in self._patch_definitions:
            self.patches[path] = patcher.start()

    def __exit__(self, type, value, traceback):
        for _, patcher in self._patch_definitions:
            patcher.stop()

class MockTestEnvironmentPosix(MockTestEnvironment):

    def __init__(self, test_case, platform_info, image_path):
        super().__init__(test_case, platform_info, image_path)

        self.patch('os.name', new='posix')

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)

        # Assert for proper image copy
        mocked_call = self.patches[
            'mbed_os_tools.test.host_tests_plugins.host_test_plugins.call'
        ]

        first_call_args = mocked_call.call_args_list[0][0][0]
        self._test_case.assertEqual(first_call_args[0], "cp")
        self._test_case.assertEqual(first_call_args[1], self._image_path)
        self._test_case.assertTrue(first_call_args[2].startswith(self._platform_info["mount_point"]))
        self._test_case.assertTrue(first_call_args[2].endswith(os.path.splitext(self._image_path)[1]))


class MockTestEnvironmentLinux(MockTestEnvironmentPosix):

    def __init__(self, test_case, platform_info, image_path):
        super().__init__(test_case, platform_info, image_path)

        self.patch(
            'os.uname',
            new=MagicMock(return_value=('Linux',)),
            create=True
        )

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)

        # Assert for proper image copy
        mocked_call = self.patches[
            'mbed_os_tools.test.host_tests_plugins.host_test_plugins.call'
        ]

        second_call_args = mocked_call.call_args_list[1][0][0]
        destination_path = os.path.normpath(
            os.path.join(
                self._platform_info["mount_point"],
                os.path.basename(self._image_path)
            )
        )

        self._test_case.assertEqual(
            second_call_args,
            ["sync", "-f", destination_path]
        )

        # Ensure only two subprocesses were started
        self._test_case.assertEqual(len(mocked_call.call_args_list), 2)

class MockTestEnvironmentDarwin(MockTestEnvironmentPosix):

    def __init__(self, test_case, platform_info, image_path):
        super().__init__(test_case, platform_info, image_path)

        self.patch(
            'os.uname',
            new=MagicMock(return_value=('Darwin',)),
            create=True
        )

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)

        # Assert for proper image copy
        mocked_call = self.patches[
            'mbed_os_tools.test.host_tests_plugins.host_test_plugins.call'
        ]

        second_call_args = mocked_call.call_args_list[1][0][0]
        self._test_case.assertEqual(second_call_args, ["sync"])

        # Ensure only two subprocesses were started
        self._test_case.assertEqual(len(mocked_call.call_args_list), 2)

class MockTestEnvironmentWindows(MockTestEnvironment):

    def __init__(self, test_case, platform_info, image_path):
        super().__init__(test_case, platform_info, image_path)

        self.patch('os.name', new='nt')

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)

        # Assert for proper image copy
        mocked_call = self.patches[
            'mbed_os_tools.test.host_tests_plugins.host_test_plugins.call'
        ]

        first_call_args = mocked_call.call_args_list[0][0][0]
        self._test_case.assertEqual(first_call_args[0], "copy")
        self._test_case.assertEqual(first_call_args[1], self._image_path)
        self._test_case.assertTrue(first_call_args[2].startswith(self._platform_info["mount_point"]))
        self._test_case.assertTrue(first_call_args[2].endswith(os.path.splitext(self._image_path)[1]))

        # Ensure only one subprocess was started
        self._test_case.assertEqual(len(mocked_call.call_args_list), 1)

mock_platform_info = {
    "platform_name": "K64F",
    "target_id": "0240000031754e45000c0018948500156461000097969900",
    "mount_point": os.path.normpath("/mnt/DAPLINK"),
    "serial_port": os.path.normpath("/dev/ttyACM0"),
}
mock_image_path = os.path.normpath(
    "BUILD/tests/K64F/GCC_ARM/TESTS/network/interface/interface.bin"
)

class BlackBoxHostTestTestCase(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def tearDown(self):
        pass

    def test_host_test_linux(self):
        with MockTestEnvironmentLinux(self, mock_platform_info, mock_image_path) as _env:
            test_selector = DefaultTestSelector(init_host_test_cli_params())
            result = test_selector.execute()
            test_selector.finish()

        self.assertEqual(result, 0)

    def test_host_test_darwin(self):
        with MockTestEnvironmentDarwin(self, mock_platform_info, mock_image_path) as _env:
            test_selector = DefaultTestSelector(init_host_test_cli_params())
            result = test_selector.execute()
            test_selector.finish()

        self.assertEqual(result, 0)

    def test_host_test_windows(self):
        with MockTestEnvironmentWindows(self, mock_platform_info, mock_image_path) as _env:
            test_selector = DefaultTestSelector(init_host_test_cli_params())
            result = test_selector.execute()
            test_selector.finish()

        self.assertEqual(result, 0)

if __name__ == '__main__':
    unittest.main()
