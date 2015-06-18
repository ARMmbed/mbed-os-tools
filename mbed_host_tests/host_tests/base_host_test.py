"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

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

class BaseHostTest():
    """ Base class for each host-test test cases with standard
        rampUp, test and rampDown set of functions
    """

    def rumpUp(self):
        """ Ramp up function, initialize your test case dynamic resources in this function
        """
        pass

    def test(self, selftest):
        """ Blocking test execution process:

            rampUp()
            test()
            rampDown()
        """
        pass

    def rampDown(self):
        """ Ramp up function, free your test case dynamic resources in this function
        """
        pass
