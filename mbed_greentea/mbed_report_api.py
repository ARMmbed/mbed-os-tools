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

def export_to_file(file_name, payload):
    """! Simple file dump used to store reports on disk
    @param file_name Report file name (with path if needed)
    @param payload Data to store inside file
    @return True if report save was successful
    """
    result = True
    try:
        with open(file_name, 'w') as f:
            f.write(payload)
    except IOError as e:
        print "Exporting report to file failed: ", str(e)
        result = False
    return result


def exporter_json(test_result_ext, test_suite_properties=None):
    """! Exports test results to indented JSON format
    @details This is a machine friendly format
    """
    import json
    return json.dumps(test_result_ext, indent=4)


def exporter_text(test_result_ext, test_suite_properties=None):
    """! Exports test results to text formatted output
    @details This is a human friendly format
    @return Tuple with table of results and result quantity summary string
    """
    from prettytable import PrettyTable
    #TODO: export to text, preferably to PrettyTable (SQL like) format
    cols = ['target', 'platform_name', 'test suite', 'result', 'elapsed_time (sec)', 'copy_method']
    pt = PrettyTable(cols)
    for col in cols:
        pt.align[col] = "l"
    pt.padding_width = 1 # One space between column edges and contents (default)

    result_dict = {}     # Used to print test suite results

    for target_name in sorted(test_result_ext):
        test_results = test_result_ext[target_name]
        row = []
        for test_name in sorted(test_results):
            test = test_results[test_name]

            # Grab quantity of each test result
            if test['single_test_result'] in result_dict:
                result_dict[test['single_test_result']] += 1
            else:
                result_dict[test['single_test_result']] = 1

            row.append(target_name)
            row.append(test['platform_name'])
            row.append(test_name)
            row.append(test['single_test_result'])
            row.append(round(test['elapsed_time'], 2))
            row.append(test['copy_method'])
            pt.add_row(row)
            row = []

    result_pt = pt.get_string()
    result_res = ' / '.join(['%s %s' % (value, key) for (key, value) in {k: v for k, v in result_dict.items() if v != 0}.iteritems()])
    return result_pt, result_res

def exporter_testcase_text(test_result_ext, test_suite_properties=None):
    """! Exports test case results to text formatted output
    @param test_result_ext Extended report from Greentea
    @param test_suite_properties Data from yotta module.json file
    @details This is a human friendly format
    @return Tuple with table of results and result quantity summary string
    """
    from prettytable import PrettyTable
    #TODO: export to text, preferably to PrettyTable (SQL like) format
    cols = ['target', 'platform_name', 'test suite', 'test case', 'passed', 'failed', 'result', 'elapsed_time (sec)']
    pt = PrettyTable(cols)
    for col in cols:
        pt.align[col] = "l"
    pt.padding_width = 1 # One space between column edges and contents (default)

    result_testcase_dict = {}   # Used to print test case results

    for target_name in sorted(test_result_ext):
        test_results = test_result_ext[target_name]
        row = []
        for test_suite_name in sorted(test_results):
            test = test_results[test_suite_name]

            # testcase_result stores info about test case results
            testcase_result = test['testcase_result']
            #   "testcase_result": {
            #       "STRINGS004": {
            #           "duration": 0.009999990463256836,
            #           "time_start": 1453073018.275,
            #           "time_end": 1453073018.285,
            #           "result": 1
            #       },

            for tc_name in sorted(testcase_result):
                duration = testcase_result[tc_name].get('duration', 0.0)
                # result = testcase_result[tc_name].get('result', 0)
                passed = testcase_result[tc_name].get('passed', 0)
                failed = testcase_result[tc_name].get('failed', 0)
                result_text = testcase_result[tc_name].get('result_text', "UNDEF")

                # Grab quantity of each test result
                if result_text in result_testcase_dict:
                    result_testcase_dict[result_text] += 1
                else:
                    result_testcase_dict[result_text] = 1

                row.append(target_name)
                row.append(test['platform_name'])
                row.append(test_suite_name)
                row.append(tc_name)
                row.append(passed)
                row.append(failed)
                row.append(result_text)
                row.append(round(duration, 2))
                pt.add_row(row)
                row = []

    result_pt = pt.get_string()
    result_res = ' / '.join(['%s %s' % (value, key) for (key, value) in {k: v for k, v in result_testcase_dict.items() if v != 0}.iteritems()])
    return result_pt, result_res

def exporter_testcase_junit(test_result_ext, test_suite_properties=None):
    """! Export test results in JUnit XML compliant format
    @param test_result_ext Extended report from Greentea
    @param test_spec Dictionary of test build names to test suite properties
    @details This function will import junit_xml library to perform report conversion
    @return String containing Junit XML formatted test result output
    """
    from junit_xml import TestSuite, TestCase

    test_suites = []

    for target_name in test_result_ext:
        test_results = test_result_ext[target_name]
        for test_suite_name in test_results:
            test = test_results[test_suite_name]

            # tc_elapsed_sec = test['elapsed_time']
            tc_stdout = str() #test['single_test_output']

            try:
                tc_stdout = test['single_test_output'].decode('unicode_escape').encode('ascii','ignore')
            except UnicodeDecodeError as e:
                err_mgs = "(UnicodeDecodeError) exporter_testcase_junit:", str(e)
                tc_stdout = err_mgs
                print err_mgs

            # testcase_result stores info about test case results
            testcase_result = test['testcase_result']
            #   "testcase_result": {
            #       "STRINGS004": {
            #           "duration": 0.009999990463256836,
            #           "time_start": 1453073018.275,
            #           "time_end": 1453073018.285,
            #           "result": 1
            #       },

            test_cases = []

            for tc_name in sorted(testcase_result.keys()):
                duration = testcase_result[tc_name].get('duration', 0.0)
                utest_log = testcase_result[tc_name].get('utest_log', '')
                result_text = testcase_result[tc_name].get('result_text', "UNDEF")

                try:
                    tc_stderr = '\n'.join(utest_log).decode('unicode_escape').encode('ascii','ignore')
                except UnicodeDecodeError as e:
                    err_mgs = "(UnicodeDecodeError) exporter_testcase_junit:" + str(e)
                    tc_stderr = err_mgs
                    print err_mgs

                tc_class = target_name + '.' + test_suite_name

                if result_text == 'SKIPPED':
                    # Skipped test cases do not have logs and we do not want to put
                    # whole log inside JUNIT for skipped test case
                    tc_stderr = str()

                tc = TestCase(tc_name, tc_class, duration, tc_stdout, tc_stderr)

                if result_text == 'FAIL':
                    tc.add_failure_info(result_text)
                elif result_text == 'SKIPPED':
                    tc.add_skipped_info(result_text)
                elif result_text != 'OK':
                    tc.add_error_info(result_text)

                test_cases.append(tc)

            ts_name = target_name
            test_build_properties = test_suite_properties[target_name] if target_name in test_suite_properties else None
            ts = TestSuite(ts_name, test_cases, properties=test_build_properties)
            test_suites.append(ts)

    return TestSuite.to_xml_string(test_suites)
