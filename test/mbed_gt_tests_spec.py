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
from mbed_greentea.tests_spec import TestSpec, TestBinary

simple_test_spec = {
    "builds": {
        "K64F-ARM": {
            "platform": "K64F",
            "toolchain": "ARM",
            "base_path": "./.build/K64F/ARM",
            "baud_rate": 115200,
            "tests": {
                "mbed-drivers-test-generic_tests":{
                    "binaries":[
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/ARM/mbed-drivers-test-generic_tests.bin"
                        }
                    ]
                },
                "mbed-drivers-test-c_strings":{
                    "binaries":[
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/ARM/mbed-drivers-test-c_strings.bin"
                        }
                    ]
                }
            }
        },
        "K64F-GCC": {
            "platform": "K64F",
            "toolchain": "GCC_ARM",
            "base_path": "./.build/K64F/GCC_ARM",
            "baud_rate": 9600,
            "tests": {
                "mbed-drivers-test-generic_tests":{
                    "binaries":[
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/GCC_ARM/mbed-drivers-test-generic_tests.bin"
                        }
                    ]
                }

            }
        }

    }
}


class TestsSpecFunctionality(unittest.TestCase):

    def setUp(self):
        self.ts_2_builds = simple_test_spec

    def tearDown(self):
        pass

    def test_example(self):
        self.assertEqual(True, True)
        self.assertNotEqual(True, False)

    def test_get_test_builds(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)
        test_builds = self.test_spec.get_test_builds()

        self.assertIs(type(test_builds), list)
        self.assertEqual(len(test_builds), 2)

    def test_get_test_builds_names(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)
        test_builds = self.test_spec.get_test_builds()
        test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

        self.assertEqual(len(test_builds_names), 2)
        self.assertIs(type(test_builds_names), list)

        self.assertIn('K64F-ARM', test_builds_names)
        self.assertIn('K64F-GCC', test_builds_names)

    def test_get_test_build(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)
        test_builds = self.test_spec.get_test_builds()
        test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

        self.assertEqual(len(test_builds_names), 2)
        self.assertIs(type(test_builds_names), list)

        self.assertNotEqual(None, self.test_spec.get_test_build('K64F-ARM'))
        self.assertNotEqual(None, self.test_spec.get_test_build('K64F-GCC'))

    def test_get_build_properties(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)
        test_builds = self.test_spec.get_test_builds()
        test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

        self.assertEqual(len(test_builds_names), 2)
        self.assertIs(type(test_builds_names), list)

        k64f_arm = self.test_spec.get_test_build('K64F-ARM')
        k64f_gcc = self.test_spec.get_test_build('K64F-GCC')

        self.assertNotEqual(None, k64f_arm)
        self.assertNotEqual(None, k64f_gcc)

        self.assertEqual('K64F', k64f_arm.get_platform())
        self.assertEqual('ARM', k64f_arm.get_toolchain())
        self.assertEqual(115200, k64f_arm.get_baudrate())

        self.assertEqual('K64F', k64f_gcc.get_platform())
        self.assertEqual('GCC_ARM', k64f_gcc.get_toolchain())
        self.assertEqual(9600, k64f_gcc.get_baudrate())

    def test_get_test_builds_properties(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)
        test_builds = self.test_spec.get_test_builds()
        test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

        self.assertIn('K64F-ARM', test_builds_names)
        self.assertIn('K64F-GCC', test_builds_names)

    def test_get_test_builds_names_filter_by_names(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)

        filter_by_names = ['K64F-ARM']
        test_builds = self.test_spec.get_test_builds(filter_by_names=filter_by_names)
        test_builds_names = [x.get_name() for x in test_builds]
        self.assertEqual(len(test_builds_names), 1)
        self.assertIn('K64F-ARM', test_builds_names)

        filter_by_names = ['K64F-GCC']
        test_builds = self.test_spec.get_test_builds(filter_by_names=filter_by_names)
        test_builds_names = [x.get_name() for x in test_builds]
        self.assertEqual(len(test_builds_names), 1)
        self.assertIn('K64F-GCC', test_builds_names)

        filter_by_names = ['SOME-PLATFORM-NAME']
        test_builds = self.test_spec.get_test_builds(filter_by_names=filter_by_names)
        test_builds_names = [x.get_name() for x in test_builds]
        self.assertEqual(len(test_builds_names), 0)

if __name__ == '__main__':
    unittest.main()
