# Copyright 2015 ARM Limited, All rights reserved
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
import time

from random import uniform
from mock import patch
from mbed_greentea import mbed_greentea_cli

class TestmbedGt(unittest.TestCase):
    """! Mbed greentea parallelisation tests
    """
    def setUp(self):
        """
        Called before test function
        :return:
        """
        pass

    def tearDown(self):
        """
        Called after test function
        :return:
        """
        pass

    @patch('mbed_greentea.mbed_greentea_cli.optparse.OptionParser')
    @patch('mbed_greentea.mbed_greentea_cli.load_ctest_testsuite')
    @patch('mbed_greentea.mbed_greentea_cli.mbed_lstools.create')
    @patch('mbed_greentea.mbed_test_api.Popen')
    def test_basic_parallel_execution(self, popen_mock, mbedLstools_mock, loadCtestTestsuite_mock, optionParser_mock):
        #runHostTest_mock.side_effect = run_host_test_mock
        popen_mock.side_effect = PopenMock
        mbedLstools_mock.side_effect = MbedsMock
        loadCtestTestsuite_mock.return_value = load_ctest_testsuite_mock()

        my_gt_opts = GtOptions(list_of_targets="frdm-k64f-gcc",
                               parallel_test_exec=3,
                               test_by_names="mbed-drivers-test-stdio",
                               use_target_ids="02400203A0811E505D7DE3D9",
                               report_junit_file_name="junitTestReport")
        OptionParserMock.static_options = my_gt_opts
        optionParser_mock.side_effect = OptionParserMock

        mbed_greentea_cli.main()

class PopenMock:
    def __init__(self, *args, **kwargs):
        self.stdout = StdOutMock()
        self.stdin = StdOutMock()

    def communicate(self):
        return "_stdout", "_stderr"

    def returncode(self):
        return 0

    def terminate(self):
        pass

    def poll(self):
        return 0


class StdOutMock:
    def __init__(self):
        self.str = """MBED: Instrumentation: 'COM11' and disk: 'E:'\nHOST: Copy image onto target...
\t1 file(s) copied.
HOST: Initialize serial port...
...port ready!
HOST: Reset target...
HOST: Detecting test case properties...
HOST: Property 'timeout' = '20'
HOST: Property 'host_test_name' = 'echo'
HOST: Property 'description' = 'serial interrupt test'
HOST: Property 'test_id' = 'MBED_14'
HOST: Start test...
...port ready!
HOST: Starting the ECHO test
..................................................
{{success}}
{{end}}"""
        self.offset = 0

    def read(self, size):
        if self.offset < len(self.str):
            ret = [self.str[i] for i in range(self.offset, self.offset + size)]
            self.offset += size
            return ''.join(ret)
        else:
            time.sleep(uniform(0.1, 2))
            self.offset = 0
            return None

    def close(self):
        pass


def run_host_test_mock(*args, **kwargs):
    random_testduration = uniform(0.1, 2)
    time.sleep(random_testduration)
    return ('OK', 'single_test_output', random_testduration, 10)


def load_ctest_testsuite_mock():
    return {'mbed-drivers-test-echo': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-echo.bin',
            'mbed-drivers-test-time_us': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-time_us.bin',
            'mbed-drivers-test-serial_interrupt': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-serial_interrupt.bin',
            'mbed-drivers-test-blinky': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-blinky.bin',
            'mbed-drivers-test-functionpointer': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-functionpointer.bin',
            'mbed-drivers-test-stdio': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-stdio.bin',
            'mbed-drivers-test-eventhandler': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-eventhandler.bin',
            'mbed-drivers-test-stl': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-stl.bin',
            'mbed-drivers-test-div': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-div.bin',
            'mbed-drivers-test-rtc': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-rtc.bin',
            'mbed-drivers-test-cstring': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-cstring.bin',
            'mbed-drivers-test-cpp': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-cpp.bin',
            'mbed-drivers-test-timeout': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-timeout.bin',
            'mbed-drivers-test-ticker_3': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-ticker_3.bin',
            'mbed-drivers-test-ticker_2': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-ticker_2.bin',
            'mbed-drivers-test-heap_and_stack': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-heap_and_stack.bin',
            'mbed-drivers-test-hello': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-hello.bin',
            'mbed-drivers-test-ticker': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-ticker.bin',
            'mbed-drivers-test-dev_null': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-dev_null.bin',
            'mbed-drivers-test-basic': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-basic.bin',
            'mbed-drivers-test-asynch_spi': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-asynch_spi.bin',
            'mbed-drivers-test-sleep_timeout': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-sleep_timeout.bin',
            'mbed-drivers-test-detect': '.\\build\\frdm-k64f-gcc\\test\\mbed-drivers-test-detect.bin'}


class GtOptions:
    def __init__(self,
                 list_of_targets,
                 test_by_names=None,
                 skip_test=None,
                 only_build_tests=False,
                 skip_yotta_build=True,
                 copy_method=None,
                 parallel_test_exec=0,
                 verbose_test_configuration_only=False,
                 build_to_release=False,
                 build_to_debug=False,
                 list_binaries=False,
                 map_platform_to_yt_target={},
                 use_target_ids=False,
                 lock_by_target=False,
                 digest_source=None,
                 json_test_configuration=None,
                 run_app=None,
                 report_junit_file_name=None,
                 report_text_file_name=None,
                 report_json=False,
                 report_fails=False,
                 verbose_test_result_only=False,
                 enum_host_tests=None,
                 yotta_search_for_mbed_target=False,
                 plain=False,
                 shuffle_test_order=False,
                 shuffle_test_seed=None,
                 verbose=True,
                 version=False):

        self.list_of_targets = list_of_targets
        self.test_by_names = test_by_names
        self.skip_test = skip_test
        self.only_build_tests = only_build_tests
        self.skip_yotta_build = skip_yotta_build
        self.copy_method = copy_method
        self.parallel_test_exec = parallel_test_exec
        self.verbose_test_configuration_only = verbose_test_configuration_only
        self.build_to_release = build_to_release
        self.build_to_debug = build_to_debug
        self.list_binaries = list_binaries
        self.map_platform_to_yt_target = map_platform_to_yt_target
        self.use_target_ids = use_target_ids
        self.lock_by_target = lock_by_target
        self.digest_source = digest_source
        self.json_test_configuration = json_test_configuration
        self.run_app = run_app
        self.report_junit_file_name = report_junit_file_name
        self.report_text_file_name = report_text_file_name
        self.report_json = report_json
        self.report_fails = report_fails
        self.verbose_test_result_only = verbose_test_result_only
        self.enum_host_tests = enum_host_tests
        self.yotta_search_for_mbed_target = yotta_search_for_mbed_target
        self.plain = plain
        self.shuffle_test_order = shuffle_test_order
        self.shuffle_test_seed = shuffle_test_seed
        self.verbose = verbose
        self.version = version


class OptionParserMock:
    static_options = {}

    def __init__(self):
        pass

    def add_option(self, *args, **kwargs):
        pass

    def parse_args(self):
        return (OptionParserMock.static_options, [])


class MbedsMock:
    def __init__(self):
        pass

    def list_mbeds(self):
        return [{'target_id_mbed_htm': '02400203A0811E505D7DE3E8', 'mount_point': 'E:', 'target_id': '02400203A0811E505D7DE3E8', 'serial_port': u'COM11', 'target_id_usb_id': '02400203A0811E505D7DE3E8', 'platform_name': 'K64F'},
                {'target_id_mbed_htm': '02400203A0811E505D7DE3D9', 'mount_point': 'F:', 'target_id': '02400203A0811E505D7DE3D9', 'serial_port': u'COM12', 'target_id_usb_id': '02400203A0811E505D7DE3D9', 'platform_name': 'K64F'}]

    def list_mbeds_ext(self):
        return [{'target_id_mbed_htm': '02400203A0811E505D7DE3E8', 'mount_point': 'E:', 'target_id': '02400203A0811E505D7DE3E8', 'serial_port': u'COM11', 'target_id_usb_id': '02400203A0811E505D7DE3E8', 'platform_name': 'K64F', 'platform_name_unique': 'K64F[0]'},
                {'target_id_mbed_htm': '02400203A0811E505D7DE3D9', 'mount_point': 'F:', 'target_id': '02400203A0811E505D7DE3D9', 'serial_port': u'COM12', 'target_id_usb_id': '02400203A0811E505D7DE3D9', 'platform_name': 'K64F', 'platform_name_unique': 'K64F[1]'},
                {'target_id_mbed_htm': '02400203A0811E505D7DE3A7', 'mount_point': 'G:', 'target_id': '02400203A0811E505D7DE3A7', 'serial_port': u'COM13', 'target_id_usb_id': '02400203A0811E505D7DE3A7', 'platform_name': 'K64F', 'platform_name_unique': 'K64F[2]'},
                {'target_id_mbed_htm': '09400203A0811E505D7DE3B6', 'mount_point': 'H:', 'target_id': '09400203A0811E505D7DE3B6', 'serial_port': u'COM14', 'target_id_usb_id': '09400203A0811E505D7DE3B6', 'platform_name': 'K100F', 'platform_name_unique': 'K100F[0]'}]

    def list_platforms_ext(self):
        return {'K64F': 2}


if __name__ == '__main__':
    unittest.main()
