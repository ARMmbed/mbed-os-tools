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

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""

class HostRegistry:
    """ Class stores registry with host tests and objects representing them
    """
    HOST_TESTS = {} # Map between host_test_name -> host_test_object

    def register_host_test(self, ht_name, ht_object):
        """! Registers host test object by name

        @param ht_name Host test unique name
        @param ht_object Host test class object
        """
        if ht_name not in self.HOST_TESTS:
            self.HOST_TESTS[ht_name] = ht_object

    def unregister_host_test(self, ht_name):
        """! Unregisters host test object by name

        @param ht_name Host test unique name
        """
        if ht_name in self.HOST_TESTS:
            del self.HOST_TESTS[ht_name]

    def get_host_test(self, ht_name):
        """! Fetches host test object by name

        @param ht_name Host test unique name

        @return Host test callable object or None if object is not found
        """
        return self.HOST_TESTS[ht_name] if ht_name in self.HOST_TESTS else None

    def is_host_test(self, ht_name):
        """! Checks (by name) if host test object is registered already

        @param ht_name Host test unique name

        @return True if ht_name is registered (available), else False
        """
        return ht_name in self.HOST_TESTS and self.HOST_TESTS[ht_name] is not None
