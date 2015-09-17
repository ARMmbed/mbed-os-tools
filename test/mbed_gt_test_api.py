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
from mbed_greentea import mbed_test_api



class GreenteaTestAPI(unittest.TestCase):

    def setUp(self):
        self.OUTPUT_FAILURE = """HOST: Reset target...
HOST: Detecting test case properties...
HOST: Property 'timeout' = '10'
HOST: Property 'host_test_name' = 'detect_auto'
HOST: Property 'description' = 'Simple detect test'
HOST: Property 'test_id' = 'DTCT_1'
HOST: Start test...
{{start}}
HOST: Detecting target name...
MBED: Target 'Unknown'
HOST: MUT Target name 'Unknown', expected 'K64F'... [FAIL]
MBED: Test ID 'Unknown'
MBED: UUID 'Unknown'

{{failure}}
{{end}}
"""

        self.OUTPUT_SUCCESS = """MBED: Instrumentation: "COM142" and disk: "E:"
HOST: Copy image onto target...
        1 file(s) copied.
HOST: Initialize serial port...
...port ready!
HOST: Reset target...
HOST: Detecting test case properties...
HOST: Property 'timeout' = '20'
HOST: Property 'host_test_name' = 'default_auto'
HOST: Property 'description' = 'Basic'
HOST: Property 'test_id' = 'MBED_A1'
HOST: Start test...
{{success}}
{{end}}
"""

        self.OUTPUT_TIMEOUT = """
"""

        self.OUTPUT_UNDEF = """
MBED: Instrumentation: "COM142" and disk: "E:"
HOST: Copy image onto target...
        1 file(s) copied.
HOST: Initialize serial port...
...port ready!
HOST: Reset target...
{{end}}
"""
    
    def tearDown(self):
        pass

    def test_get_test_result(self):
        self.assertEqual(mbed_test_api.TEST_RESULT_OK, mbed_test_api.get_test_result(self.OUTPUT_SUCCESS))
        self.assertEqual(mbed_test_api.TEST_RESULT_FAIL, mbed_test_api.get_test_result(self.OUTPUT_FAILURE))
        self.assertEqual(mbed_test_api.TEST_RESULT_TIMEOUT, mbed_test_api.get_test_result(self.OUTPUT_TIMEOUT))
        self.assertEqual(mbed_test_api.TEST_RESULT_UNDEF, mbed_test_api.get_test_result(self.OUTPUT_UNDEF))

if __name__ == '__main__':
    unittest.main()
