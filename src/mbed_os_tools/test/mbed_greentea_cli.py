
# Copyright (c) 2018, Arm Limited and affiliates.
# SPDX-License-Identifier: Apache-2.0
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

import os
import fnmatch

from .cmake_handlers import list_binaries_for_builds, list_binaries_for_targets
from .mbed_greentea_log import gt_logger
from .mbed_target_info import get_platform_property
from .mbed_test_api import run_host_test, TEST_RESULT_OK, TEST_RESULT_FAIL

RET_NO_DEVICES = 1001
RET_YOTTA_BUILD_FAIL = -1
LOCAL_HOST_TESTS_DIR = './test/host_tests'  # Used by mbedhtrun -e <dir>


def get_local_host_tests_dir(path):
    """! Forms path to local host tests. Performs additional basic checks if directory exists etc.
    """
    # If specified path exist return path
    if path and os.path.exists(path) and os.path.isdir(path):
        return path
    # If specified path is not set or doesn't exist returns default path
    if not path and os.path.exists(LOCAL_HOST_TESTS_DIR) and os.path.isdir(LOCAL_HOST_TESTS_DIR):
        return LOCAL_HOST_TESTS_DIR
    return None

def create_filtered_test_list(ctest_test_list, test_by_names, skip_test, test_spec=None):
    """! Filters test case list (filtered with switch -n) and return filtered list.
    @ctest_test_list List iof tests, originally from CTestTestFile.cmake in yotta module. Now comes from test specification
    @test_by_names Command line switch -n <test_by_names>
    @skip_test Command line switch -i <skip_test>
    @param test_spec Test specification object loaded with --test-spec switch
    @return
    """

    filtered_ctest_test_list = ctest_test_list
    test_list = None
    invalid_test_names = []
    if filtered_ctest_test_list is None:
        return {}

    if test_by_names:
        filtered_ctest_test_list = {}   # Subset of 'ctest_test_list'
        test_list = test_by_names.lower().split(',')
        gt_logger.gt_log("test case filter (specified with -n option)")

        for test_name in set(test_list):
            gt_logger.gt_log_tab(test_name)
            matches = [test for test in ctest_test_list.keys() if fnmatch.fnmatch(test, test_name)]
            if matches:
                for match in matches:
                    gt_logger.gt_log_tab("test filtered in '%s'"% gt_logger.gt_bright(match))
                    filtered_ctest_test_list[match] = ctest_test_list[match]
            else:
                invalid_test_names.append(test_name)

    if skip_test:
        test_list = skip_test.split(',')
        gt_logger.gt_log("test case filter (specified with -i option)")

        for test_name in set(test_list):
            gt_logger.gt_log_tab(test_name)
            matches = [test for test in filtered_ctest_test_list.keys() if fnmatch.fnmatch(test, test_name)]
            if matches:
                for match in matches:
                    gt_logger.gt_log_tab("test filtered out '%s'"% gt_logger.gt_bright(match))
                    del filtered_ctest_test_list[match]
            else:
                invalid_test_names.append(test_name)

    if invalid_test_names:
        opt_to_print = '-n' if test_by_names else 'skip-test'
        gt_logger.gt_log_warn("invalid test case names (specified with '%s' option)"% opt_to_print)
        for test_name in invalid_test_names:
            if test_spec:
                test_spec_name = test_spec.test_spec_filename
                gt_logger.gt_log_warn("test name '%s' not found in '%s' (specified with --test-spec option)"% (gt_logger.gt_bright(test_name),
                    gt_logger.gt_bright(test_spec_name)))
            else:
                gt_logger.gt_log_warn("test name '%s' not found in CTestTestFile.cmake (specified with '%s' option)"% (gt_logger.gt_bright(test_name),
                    opt_to_print))
        gt_logger.gt_log_tab("note: test case names are case sensitive")
        gt_logger.gt_log_tab("note: see list of available test cases below")
        # Print available test suite names (binary names user can use with -n
        if test_spec:
            list_binaries_for_builds(test_spec)
        else:
            list_binaries_for_targets()

    return filtered_ctest_test_list


def run_test_thread(test_result_queue, test_queue, opts, mut, build, build_path, greentea_hooks):
    test_exec_retcode = 0
    test_platforms_match = 0
    test_report = {}

    disk = mut['mount_point']
    port = mut['serial_port']
    micro = mut['platform_name']
    program_cycle_s = get_platform_property(micro, "program_cycle_s")
    forced_reset_timeout = get_platform_property(micro, "forced_reset_timeout")
    copy_method = get_platform_property(micro, "copy_method")
    reset_method = get_platform_property(micro, "reset_method")

    while not test_queue.empty():
        try:
            test = test_queue.get(False)
        except Exception as e:
            gt_logger.gt_log_err(str(e))
            break

        test_result = 'SKIPPED'

        if opts.copy_method:
            copy_method = opts.copy_method
        elif not copy_method:
            copy_method = 'shell'

        if opts.reset_method:
            reset_method = opts.reset_method

        verbose = opts.verbose_test_result_only
        enum_host_tests_path = get_local_host_tests_dir(opts.enum_host_tests)

        test_platforms_match += 1
        host_test_result = run_host_test(test['image_path'],
                                         disk,
                                         port,
                                         build_path,
                                         mut['target_id'],
                                         micro=micro,
                                         copy_method=copy_method,
                                         reset=reset_method,
                                         program_cycle_s=program_cycle_s,
                                         forced_reset_timeout=forced_reset_timeout,
                                         digest_source=opts.digest_source,
                                         json_test_cfg=opts.json_test_configuration,
                                         enum_host_tests_path=enum_host_tests_path,
                                         global_resource_mgr=opts.global_resource_mgr,
                                         fast_model_connection=opts.fast_model_connection,
                                         num_sync_packtes=opts.num_sync_packtes,
                                         tags=opts.tags,
                                         retry_count=opts.retry_count,
                                         polling_timeout=opts.polling_timeout,
                                         verbose=verbose)

        # Some error in htrun, abort test execution
        if isinstance(host_test_result, int):
            # int(host_test_result) > 0 - Call to mbedhtrun failed
            # int(host_test_result) < 0 - Something went wrong while executing mbedhtrun
            gt_logger.gt_log_err("run_test_thread.run_host_test() failed, aborting...")
            break

        # If execution was successful 'run_host_test' return tuple with results
        single_test_result, single_test_output, single_testduration, single_timeout, result_test_cases, test_cases_summary, memory_metrics = host_test_result
        test_result = single_test_result

        build_path_abs = os.path.abspath(build_path)

        if single_test_result != TEST_RESULT_OK:
            test_exec_retcode += 1

        if single_test_result in [TEST_RESULT_OK, TEST_RESULT_FAIL]:
            if greentea_hooks:
                # Test was successful
                # We can execute test hook just after test is finished ('hook_test_end')
                format = {
                    "test_name": test['test_bin'],
                    "test_bin_name": os.path.basename(test['image_path']),
                    "image_path": test['image_path'],
                    "build_path": build_path,
                    "build_path_abs": build_path_abs,
                    "build_name": build,
                }
                greentea_hooks.run_hook_ext('hook_test_end', format)

        # Update report for optional reporting feature
        test_suite_name = test['test_bin'].lower()
        if build not in test_report:
            test_report[build] = {}

        if test_suite_name not in test_report[build]:
            test_report[build][test_suite_name] = {}

        if not test_cases_summary and not result_test_cases:
            gt_logger.gt_log_warn("test case summary event not found")
            gt_logger.gt_log_tab("no test case report present, assuming test suite to be a single test case!")

            # We will map test suite result to test case to
            # output valid test case in report

            # Generate "artificial" test case name from test suite name#
            # E.g:
            #   mbed-drivers-test-dev_null -> dev_null
            test_case_name = test_suite_name
            test_str_idx = test_suite_name.find("-test-")
            if test_str_idx != -1:
                test_case_name = test_case_name[test_str_idx + 6:]

            gt_logger.gt_log_tab("test suite: %s"% test_suite_name)
            gt_logger.gt_log_tab("test case: %s"% test_case_name)

            # Test case result: OK, FAIL or ERROR
            tc_result_text = {
                "OK": "OK",
                "FAIL": "FAIL",
            }.get(single_test_result, 'ERROR')

            # Test case integer success code OK, FAIL and ERROR: (0, >0, <0)
            tc_result = {
                "OK": 0,
                "FAIL": 1024,
                "ERROR": -1024,
            }.get(tc_result_text, '-2048')

            # Test case passes and failures: (1 pass, 0 failures) or (0 passes, 1 failure)
            tc_passed, tc_failed = {
                0: (1, 0),
            }.get(tc_result, (0, 1))

            # Test case report build for whole binary
            # Add test case made from test suite result to test case report
            result_test_cases = {
                test_case_name: {
                        'duration': single_testduration,
                        'time_start': 0.0,
                        'time_end': 0.0,
                        'utest_log': single_test_output.splitlines(),
                        'result_text': tc_result_text,
                        'passed': tc_passed,
                        'failed': tc_failed,
                        'result': tc_result,
                    }
            }

            # Test summary build for whole binary (as a test case)
            test_cases_summary = (tc_passed, tc_failed, )

        gt_logger.gt_log("test on hardware with target id: %s"% (mut['target_id']))
        gt_logger.gt_log("test suite '%s' %s %s in %.2f sec"% (test['test_bin'],
            '.' * (80 - len(test['test_bin'])),
            test_result,
            single_testduration))

        # Test report build for whole binary
        test_report[build][test_suite_name]['single_test_result'] = single_test_result
        test_report[build][test_suite_name]['single_test_output'] = single_test_output
        test_report[build][test_suite_name]['elapsed_time'] = single_testduration
        test_report[build][test_suite_name]['platform_name'] = micro
        test_report[build][test_suite_name]['copy_method'] = copy_method
        test_report[build][test_suite_name]['testcase_result'] = result_test_cases
        test_report[build][test_suite_name]['memory_metrics'] = memory_metrics

        test_report[build][test_suite_name]['build_path'] = build_path
        test_report[build][test_suite_name]['build_path_abs'] = build_path_abs
        test_report[build][test_suite_name]['image_path'] = test['image_path']
        test_report[build][test_suite_name]['test_bin_name'] = os.path.basename(test['image_path'])

        passes_cnt, failures_cnt = 0, 0
        for tc_name in sorted(result_test_cases.keys()):
            gt_logger.gt_log_tab("test case: '%s' %s %s in %.2f sec"% (tc_name,
                '.' * (80 - len(tc_name)),
                result_test_cases[tc_name].get('result_text', '_'),
                result_test_cases[tc_name].get('duration', 0.0)))
            if result_test_cases[tc_name].get('result_text', '_') == 'OK':
                passes_cnt += 1
            else:
                failures_cnt += 1

        if test_cases_summary:
            passes, failures = test_cases_summary
            gt_logger.gt_log("test case summary: %d pass%s, %d failur%s"% (passes,
                '' if passes == 1 else 'es',
                failures,
                'e' if failures == 1 else 'es'))
            if passes != passes_cnt or failures != failures_cnt:
                gt_logger.gt_log_err("utest test case summary mismatch: utest reported passes and failures miscount!")
                gt_logger.gt_log_tab("reported by utest: passes = %d, failures %d)"% (passes, failures))
                gt_logger.gt_log_tab("test case result count: passes = %d, failures %d)"% (passes_cnt, failures_cnt))

        if single_test_result != 'OK' and not verbose and opts.report_fails:
            # In some cases we want to print console to see why test failed
            # even if we are not in verbose mode
            gt_logger.gt_log_tab("test failed, reporting console output (specified with --report-fails option)")
            print
            print(single_test_output)

    #greentea_release_target_id(mut['target_id'], gt_instance_uuid)
    test_result_queue.put({'test_platforms_match': test_platforms_match,
                           'test_exec_retcode': test_exec_retcode,
                           'test_report': test_report})
    return
