#!/usr/bin/env python

"""
mbed SDK
Copyright (c) 2011-2014 ARM Limited

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

import os
import sys
import optparse

from mbed_test_api import run_host_test
from mbed_test_api import run_cli_command
from mbed_test_api import TEST_RESULTS
from mbed_test_api import TEST_RESULT_OK
from cmake_handlers import load_ctest_testsuite
from cmake_handlers import list_binaries_for_targets
from mbed_report_api import exporter_junit
from mbed_target_info import get_mbed_clasic_target_info
from mbed_target_info import get_mbed_supported_test
from mbed_target_info import get_mbed_target_from_current_dir


try:
    import mbed_lstools
    import mbed_host_tests
except:
    pass

MBED_LMTOOLS = 'mbed_lstools' in sys.modules
MBED_HOST_TESTS = 'mbed_host_tests' in sys.modules


def main():
    """! This is main CLI function with all command line parameters

    @details This function also implements CLI workflow depending on CLI parameters inputed

    @return This function doesn't return, it exits to environment with proper success code
    """
    if not MBED_LMTOOLS:
        print "Error: mbed-lstools mbed proprietary module not installed"
        exit(-1)

    if not MBED_HOST_TESTS:
        print "Error: mbed-host-tests mbed proprietary module not installed"
        exit(-1)

    parser = optparse.OptionParser()

    parser.add_option('', '--target',
                    dest='list_of_targets',
                    help='You can specify list of targets you want to build. Use comma to sepatate them')

    parser.add_option('-n', '--test-by-names',
                      dest='test_by_names',
                      help='Runs only test enumerated it this switch. Use comma to separate test case names.')

    parser.add_option("-O", "--only-build",
                    action="store_true",
                    dest="only_build_tests",
                    default=False,
                    help="Only build repository and tests, skips actual test procedures (flashing etc.)")

    copy_methods_str = "Plugin support: " + ', '.join(mbed_host_tests.host_tests_plugins.get_plugin_caps('CopyMethod'))
    parser.add_option("-c", "--copy",
                    dest="copy_method",
                    help="Copy (flash the target) method selector. " + copy_methods_str,
                    metavar="COPY_METHOD")

    parser.add_option('', '--config',
                    dest='verbose_test_configuration_only',
                    default=False,
                    action="store_true",
                    help='Displays connected boards and detected targets and exits.')

    parser.add_option('', '--release',
                    dest='build_to_release',
                    default=False,
                    action="store_true",
                    help='If possible force build in release mode (yotta -r).')

    parser.add_option('', '--debug',
                    dest='build_to_debug',
                    default=False,
                    action="store_true",
                    help='If possible force build in debug mode (yotta -d).')

    parser.add_option('', '--list',
                    dest='list_binaries',
                    default=False,
                    action="store_true",
                    help='List available binaries')

    parser.add_option('', '--digest',
                    dest='digest_source',
                    help='Redirect input from where test suite should take console input. You can use stdin or file name to get test case console output')

    parser.add_option('', '--test-cfg',
                    dest='json_test_configuration',
                    help='Pass to host test data about host test configuration')

    parser.add_option('', '--run',
                    dest='run_app',
                    help='Flash, reset and dump serial from selected binary application')

    parser.add_option('', '--report-junit',
                    dest='report_junit_file_name',
                    help='You can log test suite results in form of JUnit compliant XML report')

    parser.add_option('-V', '--verbose-test-result',
                    dest='verbose_test_result_only',
                    default=False,
                    action="store_true",
                    help='Prints test serial output')

    parser.add_option('-v', '--verbose',
                    dest='verbose',
                    default=False,
                    action="store_true",
                    help='Verbose mode (prints some extra information)')

    parser.description = """This automated test script is used to test mbed SDK 3.0 on mbed-enabled deviecs with support from yotta build tool"""
    parser.epilog = """Example: mbedgt --auto --target frdm-k64f-gcc"""

    (opts, args) = parser.parse_args()

    # List available test binaries (names, no extension)
    if opts.list_binaries:
        list_binaries_for_targets()
        exit(0)

    # Capture alternative test console inputs, used e.g. in 'yotta test command'
    if opts.digest_source:
        host_test_result = run_host_test(image_path=None, disk=None, port=None,
                                    digest_source=opts.digest_source,
                                    verbose=opts.verbose_test_result_only)
        single_test_result, single_test_output, single_testduration, single_timeout = host_test_result
        status = TEST_RESULTS.index(single_test_result) if single_test_result in TEST_RESULTS else -1
        sys.exit(status)

    # mbed-enabled devices auto-detection procedures
    mbeds = mbed_lstools.create()
    mbeds_list = mbeds.list_mbeds()

    current_target = get_mbed_target_from_current_dir()
    print "mbedgt: current yotta target is: %s"% (current_target if current_target is not None else 'not set')

    if opts.list_of_targets is None:
        if current_target is not None:
            opts.list_of_targets = current_target.split(',')[0]

    print "mbed-ls: detecting connected mbed-enabled devices... %s"% ("no devices detected" if not len(mbeds_list) else "")
    list_of_targets = opts.list_of_targets.split(',') if opts.list_of_targets is not None else None

    test_report = {}    # Test report used to export to Junit, HTML etc...

    if opts.list_of_targets is None:
        print "mbedgt: assuming default target to be '%s'"% (current_target)
        print "\treason: no --target switch set"
        list_of_targets = [current_target]

    test_exec_retcode = 0   # Decrement this value each time test case result is not 'OK'

    for mut in mbeds_list:
        print "\tdetected %s, console at: %s, mounted at: %s"% (mut['platform_name'],
            mut['serial_port'],
            mut['mount_point'])

        # Check if mbed classic target name can be translated to yotta target name
        print "mbedgt: scan available targets for '%s' platform..."% (mut['platform_name'])
        mut_info = get_mbed_clasic_target_info(mut['platform_name'])

        if mut_info is not None:
            for yotta_target in mut_info['yotta_targets']:
                yotta_target_name = yotta_target['yotta_target']

                # Configuration print mode:
                if opts.verbose_test_configuration_only:
                    continue

                # Demo mode: --run implementation (already added --run to mbedhtrun)
                # We want to pass file name to mbedhtrun (--run NAME  =>  -f NAME_ and run only one binary
                if opts.run_app and yotta_target_name in list_of_targets:
                    print "mbedgt: running '%s' for '%s'"% (opts.run_app, yotta_target_name)
                    disk = mut['mount_point']
                    port = mut['serial_port']
                    micro = mut['platform_name']
                    program_cycle_s = mut_info['properties']['program_cycle_s']
                    copy_method = opts.copy_method if opts.copy_method else 'shell'
                    verbose = opts.verbose_test_result_only

                    host_test_result = run_host_test(opts.run_app, disk, port,
                                                micro=micro,
                                                copy_method=copy_method,
                                                program_cycle_s=program_cycle_s,
                                                digest_source=opts.digest_source,
                                                json_test_cfg=opts.json_test_configuration,
                                                run_app=opts.run_app,
                                                verbose=True)
                    single_test_result, single_test_output, single_testduration, single_timeout = host_test_result
                    status = TEST_RESULTS.index(single_test_result) if single_test_result in TEST_RESULTS else -1
                    if single_test_result != TEST_RESULT_OK:
                        test_exec_retcode -= 1
                    continue

                # Regression test mode:
                # Building sources for given target and perform normal testing
                if yotta_target_name in list_of_targets:
                    print "mbedgt: using '%s' target, prepare to build"% yotta_target_name
                    cmd = ['yotta'] # "yotta %s --target=%s,* build"% (yotta_verbose, yotta_target_name)
                    if opts.verbose is not None: cmd.append('-v')
                    cmd.append('--target=%s,*' % yotta_target_name)
                    cmd.append('build')
                    if opts.build_to_release:
                        cmd.append('-r')
                    elif opts.build_to_debug:
                        cmd.append('-d')

                    print "mbedgt: calling yotta to build your sources and tests: %s" % (' '.join(cmd))
                    yotta_result = run_cli_command(cmd, shell=False, verbose=opts.verbose)

                    print "mbedgt: yotta build %s"% ('successful' if yotta_result else 'failed')
                    # Build phase will be followed by test execution for each target
                    if yotta_result and not opts.only_build_tests:
                        binary_type = mut_info['properties']['binary_type']
                        ctest_test_list = load_ctest_testsuite(os.path.join('.', 'build', yotta_target_name),
                            binary_type=binary_type)

                        print "mbedgt: running tests for '%s' target" % yotta_target_name
                        test_list = None
                        if opts.test_by_names:
                            test_list = opts.test_by_names.lower().split(',')
                            print "mbedgt: test case filter: %s (specified with -n option)" % ', '.join(["'%s'"% t for t in test_list])

                            for test_n in test_list:
                                if test_n not in ctest_test_list:
                                    print "\ttest name '%s' not found (specified with -n option)"% test_n

                        for test_bin, image_path in ctest_test_list.iteritems():
                            test_result = 'SKIPPED'
                            # Skip test not mentioned in -n option
                            if opts.test_by_names:
                                if test_bin.lower() not in test_list:
                                    continue

                            if get_mbed_supported_test(test_bin):
                                disk = mut['mount_point']
                                port = mut['serial_port']
                                micro = mut['platform_name']
                                program_cycle_s = mut_info['properties']['program_cycle_s']
                                copy_method = opts.copy_method if opts.copy_method else 'shell'
                                verbose = opts.verbose_test_result_only

                                print "\trunning host test..."
                                host_test_result = run_host_test(image_path, disk, port,
                                    micro=micro,
                                    copy_method=copy_method,
                                    program_cycle_s=program_cycle_s,
                                    digest_source=opts.digest_source,
                                    json_test_cfg=opts.json_test_configuration,
                                    verbose=verbose)
                                single_test_result, single_test_output, single_testduration, single_timeout = host_test_result
                                test_result = single_test_result
                                if single_test_result != TEST_RESULT_OK:
                                    test_exec_retcode -= 1

                                # Update report for optional reporting feature
                                test_name = test_bin.lower()
                                if yotta_target_name not in test_report:
                                    test_report[yotta_target_name] = {}
                                if test_name not in test_report[yotta_target_name]:
                                    test_report[yotta_target_name][test_name] = {}

                                test_report[yotta_target_name][test_name]['single_test_result'] = single_test_result
                                test_report[yotta_target_name][test_name]['single_test_output'] = single_test_output
                                test_report[yotta_target_name][test_name]['elapsed_time'] = single_testduration

                                print "\ttest '%s' %s"% (test_bin, '.' * (80 - len(test_bin))),
                                print " %s in %.2f sec"% (test_result, single_testduration)
                    # We need to stop executing if yotta build fails
                    if not yotta_result:
                        print "mbedgt: yotta build failed!"
                        exit(int(ord('y')))
        else:
            print "mbed-ls: mbed classic target name '%s' is not in target database"% (mut['platform_name'])

    if opts.report_junit_file_name:
        junit_report = exporter_junit(test_report)
        with open(opts.report_junit_file_name, 'w') as f:
            f.write(junit_report)

    if opts.verbose_test_configuration_only:
        print
        print "Example: execute 'mbedgt --target=TARGET_NAME' to start testing for TARGET_NAME target"

    exit(test_exec_retcode)
