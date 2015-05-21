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

import re
import os
import os.path


def load_ctest_testsuite(link_target, binary_type='.bin', verbose=False):
    """ Loads CMake.CTest formatted data about tests from test directory

        Example path with CTestTestFile.cmake:
        c:/temp/xxx/mbed-sdk-private/build/frdm-k64f-gcc/test/

        Example format of CTestTestFile.cmake:
        # CMake generated Testfile for
        # Source directory: c:/temp/xxx/mbed-sdk-private/build/frdm-k64f-gcc/test
        # Build directory: c:/temp/xxx/mbed-sdk-private/build/frdm-k64f-gcc/test
        #
        # This file includes the relevant testing commands required for
        # testing this directory and lists subdirectories to be tested as well.
        add_test(mbed-test-stdio "mbed-test-stdio")
        add_test(mbed-test-call_before_main "mbed-test-call_before_main")
        add_test(mbed-test-dev_null "mbed-test-dev_null")
        add_test(mbed-test-div "mbed-test-div")
        add_test(mbed-test-echo "mbed-test-echo")
        add_test(mbed-test-ticker "mbed-test-ticker")
        add_test(mbed-test-hello "mbed-test-hello")

    """
    result = {}
    add_test_pattern = '[adtesADTES_]{8}\([\w\d_-]+ \"([\w\d_-]+)\"'
    re_ptrn = re.compile(add_test_pattern)
    if link_target is not None:
        ctest_path = os.path.join(link_target, 'test', 'CTestTestfile.cmake')
        try:
            with open(ctest_path) as ctest_file:
                for line in ctest_file:
                    if line.lower().startswith('add_test'):
                        m = re_ptrn.search(line)
                        if m and len(m.groups()) > 0:
                            if verbose:
                                print m.group(1) + binary_type
                            result[m.group(1)] = os.path.join(link_target, 'test', m.group(1) + binary_type)
        except:
            pass    # Return empty list if path is not found
    return result

def list_binaries_for_targets(build_dir='./build'):
    """ Prints tests in target directories, only if tests exist.
        Skips empty / no tests for target directories.
    """
    dir = build_dir
    sub_dirs = [os.path.join(dir, o) for o in os.listdir(dir) if os.path.isdir(os.path.join(dir, o))]
    print "mbedgt: available tests for built targets"
    for sub_dir in sub_dirs:
        test_list = load_ctest_testsuite(sub_dir, binary_type='')
        if len(test_list):
            print "target '%s':" % sub_dir.split(os.sep)[-1]
            for test in test_list:
                print "\ttest '%s'" % test
    print
    print "Example: execute 'mbedgt --target=TARGET_NAME -n TEST_NAME' to run TEST_NAME test only"
