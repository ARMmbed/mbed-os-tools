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

from mbed_host_tests.host_tests_registry import HostRegistry


class HostTestClassMock:
    def test(self, selftest):
        return None


class HostRegistryTestCase(unittest.TestCase):

    def setUp(self):
        self.HOSTREGISTRY = HostRegistry()

    def tearDown(self):
        pass

    def test_host_test_class_has_test_attr(self):
        """ Check if host test has 'test' class member
        """
        for i, ht_name in enumerate(self.HOSTREGISTRY.HOST_TESTS):
            ht = self.HOSTREGISTRY.HOST_TESTS[ht_name]
            if ht is not None:
                self.assertEqual(True, hasattr(ht, 'test'))

    def test_host_test_class_test_attr_callable(self):
        """ Check if host test has callable 'test' class member
            Example:
                def test(self, selftest)
        """
        for i, ht_name in enumerate(self.HOSTREGISTRY.HOST_TESTS):
            ht = self.HOSTREGISTRY.HOST_TESTS[ht_name]
            if ht is not None:
                self.assertEqual(True, hasattr(ht, 'test') and callable(getattr(ht, 'test')))

    def test_host_test_class_test_attr_callable_args_num(self):
        """ Check if host test has callable 'test' class member has 2 arguments
            Example:
                def test(self, selftest)
        """
        for i, ht_name in enumerate(self.HOSTREGISTRY.HOST_TESTS):
            ht = self.HOSTREGISTRY.HOST_TESTS[ht_name]
            if ht is not None and hasattr(ht, 'test') and callable(getattr(ht, 'test')):
                self.assertEqual(2, ht.test.func_code.co_argcount)

    def test_host_test_class_test_attr_callable_args_names(self):
        """ Check if host test has callable 'test' class member has 2 arguments called 'self' and 'selftest'
            Example:
                def test(self, selftest)
        """
        for i, ht_name in enumerate(self.HOSTREGISTRY.HOST_TESTS):
            ht = self.HOSTREGISTRY.HOST_TESTS[ht_name]
            if ht is not None and hasattr(ht, 'test') and callable(getattr(ht, 'test')) and ht.test.func_code.co_argcount == 2:
                self.assertEqual(('self', 'selftest'), ht.test.func_code.co_varnames[:ht.test.func_code.co_argcount])


if __name__ == '__main__':
    unittest.main()
