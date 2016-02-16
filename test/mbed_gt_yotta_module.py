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
from mbed_greentea.mbed_yotta_module_parse import YottaModule


class YOttaConfigurationParse(unittest.TestCase):

    def setUp(self):
        self.YOTTA_MODULE_LONG = {
            "name": "utest",
            "version": "1.9.1",
            "description": "Simple test harness with unity and greentea integration.",
            "keywords": [
                "greentea",
                "testing",
                "unittest",
                "unity",
                "unit",
                "test",
                "asynchronous",
                "async",
                "mbed-official"
                ],
            "author": "Niklas Hauser <niklas.hauser@arm.com>",
            "license": "Apache-2.0",
            "dependencies": {
                "minar": "^1.0.0",
                "core-util": "^1.0.1",
                "compiler-polyfill": "^1.2.0",
                "mbed-drivers": "~0.12.0",
                "greentea-client": "^0.1.2"
                },
            "testDependencies": {
                "unity": "^2.0.1",
                "greentea-client": "^0.1.2"
                }
        }

        self.yotta_module = YottaModule()
        self.yotta_module.set_yotta_module(self.YOTTA_MODULE_LONG)

    def tearDown(self):
        pass

    def test_get_name(self):
        self.assertEqual('utest', self.yotta_module.get_name())

    def test_get_dict_items(self):
        self.assertEqual('Simple test harness with unity and greentea integration.', self.yotta_module.get_data().get('description'))
        self.assertEqual('Apache-2.0', self.yotta_module.get_data().get('license'))

if __name__ == '__main__':
    unittest.main()
