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
from mbed_greentea import cmake_handlers

class GreenteaCmakeHandlers(unittest.TestCase):
    """ Basic true asserts to see that testing is executed
    """

    def setUp(self):
        self.ctesttestfile = """# CMake generated Testfile for
# Source directory: c:/Work2/mbed-client/test
# Build directory: c:/Work2/mbed-client/build/frdm-k64f-gcc/test
#
# This file includes the relevant testing commands required for
# testing this directory and lists subdirectories to be tested as well.
add_test(mbed-client-test-mbedclient-smokeTest "mbed-client-test-mbedclient-smokeTest")
add_test(mbed-client-test-helloworld-mbedclient "mbed-client-test-helloworld-mbedclient")
"""

    def tearDown(self):
        pass

    def test_example(self):
        self.assertEqual(True, True)
        self.assertNotEqual(True, False)

    def test_parse_ctesttestfile_line(self):
        LINK_TARGET = '/dir/to/target'
        BINARY_TYPE = '.bin'

        result = {}
        no_skipped_lines = 0
        for line in self.ctesttestfile.splitlines():
            line_parse = cmake_handlers.parse_ctesttestfile_line(LINK_TARGET, BINARY_TYPE, line, verbose=False)
            if line_parse:
                test_case, test_case_path = line_parse
                result[test_case] = test_case_path
            else:
                no_skipped_lines += 1

        self.assertIn('mbed-client-test-mbedclient-smokeTest', result)
        self.assertIn('mbed-client-test-helloworld-mbedclient', result)

        for test_case, test_case_path in result.iteritems():
            self.assertEqual(test_case_path.startswith(LINK_TARGET), True)
            self.assertEqual(test_case_path.endswith(BINARY_TYPE), True)

        self.assertEqual(len(result), 2)        # We parse two entries
        self.assertEqual(no_skipped_lines, 6)   # We skip six lines in this file

if __name__ == '__main__':
    unittest.main()
