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

Author: Przemyslaw Wirkus <Przemyslaw.wirkus@arm.com>
"""


def exporter_junit(test_result_ext, test_suite_properties=None):
    """! Export test results in JUnit XML compliant format

    @details This function will import junit_xml library to perform report conversion

    @return String containing Junit XML formatted test result output
    """
    from junit_xml import TestSuite, TestCase

    test_suites = []
    test_cases = []

    targets = sorted(test_result_ext.keys())
    for target in targets:
        test_cases = []
        tests = sorted(test_result_ext[target].keys())
        for test in tests:
            test_results = test_result_ext[target][test]
            classname = 'test.%s.%s' % (target, test)
            elapsed_sec = test_results['elapsed_time']
            _stdout = test_results['single_test_output']
            _stderr = ''
            # Test case
            tc = TestCase(test, classname, elapsed_sec, _stdout, _stderr)
            # Test case extra failure / error info
            if test_results['single_test_result'] == 'FAIL':
                message = test_results['single_test_result']
                tc.add_failure_info(message, _stdout)
            elif test_results['single_test_result'] != 'OK':
                message = test_results['single_test_result']
                tc.add_error_info(message, _stdout)

            test_cases.append(tc)
        ts = TestSuite("test.suite.%s" % target, test_cases)
        test_suites.append(ts)
    return TestSuite.to_xml_string(test_suites)


def exporter_text(test_result_ext, test_suite_properties=None):
    """! Exports test results to text formated output

    @details This is a humab friendly format
    """
    #from prettytable import PrettyTable
    #TODO: export to text, preferably to PrettyTable (SQL like) format
    pass
