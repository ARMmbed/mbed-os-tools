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
        self.OUTPUT_FAILURE = """mbedgt: mbed-host-test-runner: started
[1459245784.59][CONN][RXD] >>> Test cases: 7 passed, 1 failed with reason 'Test Cases Failed'
[1459245784.61][CONN][RXD] >>> TESTS FAILED!
[1459245784.64][CONN][INF] found KV pair in stream: {{__testcase_summary;7;1}}, queued...
[1459245784.64][CONN][RXD] {{__testcase_summary;7;1}}
[1459245784.66][CONN][INF] found KV pair in stream: {{end;failure}}, queued...
[1459245784.66][HTST][INF] __notify_complete(False)
[1459245784.66][HTST][INF] test suite run finished after 2.37 sec...
[1459245784.66][CONN][RXD] {{end;failure}}
[1459245784.67][HTST][INF] CONN exited with code: 0
[1459245784.67][HTST][INF] Some events in queue
[1459245784.67][HTST][INF] stopped consuming events
[1459245784.67][HTST][INF] host test result() call skipped, received: False
[1459245784.67][HTST][WRN] missing __exit event from DUT
[1459245784.67][HTST][INF] calling blocking teardown()
[1459245784.67][HTST][INF] teardown() finished
[1459245784.67][HTST][INF] {{result;failure}}
"""

        self.OUTPUT_SUCCESS = """mbedgt: mbed-host-test-runner: started
[1459245860.90][CONN][RXD] {{__testcase_summary;4;0}}
[1459245860.92][CONN][INF] found KV pair in stream: {{end;success}}, queued...
[1459245860.92][CONN][RXD] {{end;success}}
[1459245860.92][HTST][INF] __notify_complete(True)
[1459245860.92][HTST][INF] test suite run finished after 0.90 sec...
[1459245860.94][HTST][INF] CONN exited with code: 0
[1459245860.94][HTST][INF] No events in queue
[1459245860.94][HTST][INF] stopped consuming events
[1459245860.94][HTST][INF] host test result() call skipped, received: True
[1459245860.94][HTST][WRN] missing __exit event from DUT
[1459245860.94][HTST][INF] calling blocking teardown()
[1459245860.94][HTST][INF] teardown() finished
[1459245860.94][HTST][INF] {{result;success}}
"""

        self.OUTPUT_TIMEOUT = """mbedgt: mbed-host-test-runner: started
[1459246047.80][HTST][INF] copy image onto target...
        1 file(s) copied.
[1459246055.05][HTST][INF] starting host test process...
[1459246055.47][CONN][INF] starting connection process...
[1459246055.47][CONN][INF] initializing serial port listener...
[1459246055.47][SERI][INF] serial(port=COM205, baudrate=9600)
[1459246055.47][SERI][INF] reset device using 'default' plugin...
[1459246055.73][SERI][INF] wait for it...
[1459246056.74][CONN][INF] sending preamble '56bdcd85-b88a-460b-915e-1b9b41713b5a'...
[1459246056.74][SERI][TXD] mbedmbedmbedmbedmbedmbedmbedmbedmbedmbed
[1459246056.74][SERI][TXD] {{__sync;56bdcd85-b88a-460b-915e-1b9b41713b5a}}
[1459246065.06][HTST][INF] test suite run finished after 10.00 sec...
[1459246065.07][HTST][INF] CONN exited with code: 0
[1459246065.07][HTST][INF] No events in queue
[1459246065.07][HTST][INF] stopped consuming events
[1459246065.07][HTST][INF] host test result(): None
[1459246065.07][HTST][WRN] missing __exit event from DUT
[1459246065.07][HTST][ERR] missing __exit event from DUT and no result from host test, timeout...
[1459246065.07][HTST][INF] calling blocking teardown()
[1459246065.07][HTST][INF] teardown() finished
[1459246065.07][HTST][INF] {{result;timeout}}
"""

        self.OUTPUT_UNDEF = """mbedgt: mbed-host-test-runner: started
{{result;some_random_value}}
"""

        self.OUTOUT_CSTRING_TEST = """
[1459246264.88][HTST][INF] copy image onto target...
        1 file(s) copied.
[1459246272.76][HTST][INF] starting host test process...
[1459246273.18][CONN][INF] starting connection process...
[1459246273.18][CONN][INF] initializing serial port listener...
[1459246273.18][SERI][INF] serial(port=COM205, baudrate=9600)
[1459246273.18][SERI][INF] reset device using 'default' plugin...
[1459246273.43][SERI][INF] wait for it...
[1459246274.43][CONN][INF] sending preamble '5daa5ff9-a9c1-4b47-88a2-9295f1de7c64'...
[1459246274.43][SERI][TXD] mbedmbedmbedmbedmbedmbedmbedmbedmbedmbed
[1459246274.43][SERI][TXD] {{__sync;5daa5ff9-a9c1-4b47-88a2-9295f1de7c64}}
[1459246274.58][CONN][INF] found SYNC in stream: {{__sync;5daa5ff9-a9c1-4b47-88a2-9295f1de7c64}}, queued...
[1459246274.58][CONN][RXD] {{__sync;5daa5ff9-a9c1-4b47-88a2-9295f1de7c64}}
[1459246274.58][HTST][INF] sync KV found, uuid=5daa5ff9-a9c1-4b47-88a2-9295f1de7c64, timestamp=1459246274.575000
[1459246274.60][CONN][INF] found KV pair in stream: {{__version;1.1.0}}, queued...
[1459246274.60][CONN][RXD] {{__version;1.1.0}}
[1459246274.60][HTST][INF] DUT greentea-client version: 1.1.0
[1459246274.61][CONN][INF] found KV pair in stream: {{__timeout;5}}, queued...
[1459246274.61][HTST][INF] setting timeout to: 5 sec
[1459246274.62][CONN][RXD] {{__timeout;5}}
[1459246274.64][CONN][INF] found KV pair in stream: {{__host_test_name;default_auto}}, queued...
[1459246274.64][HTST][INF] host test setup() call...
[1459246274.64][HTST][INF] CALLBACKs updated
[1459246274.64][HTST][INF] host test detected: default_auto
[1459246274.64][CONN][RXD] {{__host_test_name;default_auto}}
[1459246274.66][CONN][INF] found KV pair in stream: {{__testcase_count;8}}, queued...
[1459246274.66][CONN][RXD] {{__testcase_count;8}}
[1459246274.69][CONN][RXD] >>> Running 8 test cases...
[1459246274.74][CONN][RXD] >>> Running case #1: 'C strings: strtok'...
[1459246274.79][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: strtok}}, queued...
[1459246274.79][CONN][RXD] {{__testcase_start;C strings: strtok}}
[1459246274.84][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: strtok;1;0}}, queued...
[1459246274.84][CONN][RXD] {{__testcase_finish;C strings: strtok;1;0}}
[1459246274.88][CONN][RXD] >>> 'C strings: strtok': 1 passed, 0 failed
[1459246274.93][CONN][RXD] >>> Running case #2: 'C strings: strpbrk'...
[1459246274.97][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: strpbrk}}, queued...
[1459246274.97][CONN][RXD] {{__testcase_start;C strings: strpbrk}}
[1459246275.01][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: strpbrk;1;0}}, queued...
[1459246275.01][CONN][RXD] {{__testcase_finish;C strings: strpbrk;1;0}}
[1459246275.06][CONN][RXD] >>> 'C strings: strpbrk': 1 passed, 0 failed
[1459246275.13][CONN][RXD] >>> Running case #3: 'C strings: %i %d integer formatting'...
[1459246275.18][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %i %d integer formatting}}, queued...
[1459246275.18][CONN][RXD] {{__testcase_start;C strings: %i %d integer formatting}}
[1459246275.24][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %i %d integer formatting;1;0}}, queued...
[1459246275.24][CONN][RXD] {{__testcase_finish;C strings: %i %d integer formatting;1;0}}
[1459246275.32][CONN][RXD] >>> 'C strings: %i %d integer formatting': 1 passed, 0 failed
[1459246275.38][CONN][RXD] >>> Running case #4: 'C strings: %u %d integer formatting'...
[1459246275.44][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %u %d integer formatting}}, queued...
[1459246275.44][CONN][RXD] {{__testcase_start;C strings: %u %d integer formatting}}
[1459246275.50][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %u %d integer formatting;1;0}}, queued...
[1459246275.50][CONN][RXD] {{__testcase_finish;C strings: %u %d integer formatting;1;0}}
[1459246275.57][CONN][RXD] >>> 'C strings: %u %d integer formatting': 1 passed, 0 failed
[1459246275.64][CONN][RXD] >>> Running case #5: 'C strings: %x %E integer formatting'...
[1459246275.68][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %x %E integer formatting}}, queued...
[1459246275.68][CONN][RXD] {{__testcase_start;C strings: %x %E integer formatting}}
[1459246275.74][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %x %E integer formatting;1;0}}, queued...
[1459246275.74][CONN][RXD] {{__testcase_finish;C strings: %x %E integer formatting;1;0}}
[1459246275.82][CONN][RXD] >>> 'C strings: %x %E integer formatting': 1 passed, 0 failed
[1459246275.88][CONN][RXD] >>> Running case #6: 'C strings: %f %f float formatting'...
[1459246275.94][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %f %f float formatting}}, queued...
[1459246275.94][CONN][RXD] {{__testcase_start;C strings: %f %f float formatting}}
[1459246276.10][CONN][RXD] :57::FAIL: Expected '0.002000 0.924300 15.913200 791.773680 6208.200000 25719.495200 426815.982588 6429271.046000 42468024.930000 212006462.910000' Was '
'
[1459246276.18][CONN][RXD] >>> failure with reason 'Assertion Failed' during 'Case Handler'
[1459246276.25][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %f %f float formatting;0;1}}, queued...
[1459246276.25][CONN][RXD] {{__testcase_finish;C strings: %f %f float formatting;0;1}}
[1459246276.34][CONN][RXD] >>> 'C strings: %f %f float formatting': 0 passed, 1 failed with reason 'Test Cases Failed'
[1459246276.41][CONN][RXD] >>> Running case #7: 'C strings: %e %E float formatting'...
[1459246276.46][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %e %E float formatting}}, queued...
[1459246276.46][CONN][RXD] {{__testcase_start;C strings: %e %E float formatting}}
[1459246276.52][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %e %E float formatting;1;0}}, queued...
[1459246276.53][CONN][RXD] {{__testcase_finish;C strings: %e %E float formatting;1;0}}
[1459246276.59][CONN][RXD] >>> 'C strings: %e %E float formatting': 1 passed, 0 failed
[1459246276.65][CONN][RXD] >>> Running case #8: 'C strings: %g %g float formatting'...
[1459246276.71][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %g %g float formatting}}, queued...
[1459246276.71][CONN][RXD] {{__testcase_start;C strings: %g %g float formatting}}
[1459246276.77][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %g %g float formatting;1;0}}, queued...
[1459246276.77][CONN][RXD] {{__testcase_finish;C strings: %g %g float formatting;1;0}}
[1459246276.83][CONN][RXD] >>> 'C strings: %g %g float formatting': 1 passed, 0 failed
[1459246276.90][CONN][RXD] >>> Test cases: 7 passed, 1 failed with reason 'Test Cases Failed'
[1459246276.92][CONN][RXD] >>> TESTS FAILED!
[1459246276.95][CONN][INF] found KV pair in stream: {{__testcase_summary;7;1}}, queued...
[1459246276.95][CONN][RXD] {{__testcase_summary;7;1}}
[1459246276.97][CONN][INF] found KV pair in stream: {{end;failure}}, queued...
[1459246276.97][CONN][RXD] {{end;failure}}
[1459246276.97][HTST][INF] __notify_complete(False)
[1459246276.97][HTST][INF] test suite run finished after 2.37 sec...
[1459246276.98][HTST][INF] CONN exited with code: 0
[1459246276.98][HTST][INF] Some events in queue
[1459246276.98][HTST][INF] stopped consuming events
[1459246276.98][HTST][INF] host test result() call skipped, received: False
[1459246276.98][HTST][WRN] missing __exit event from DUT
[1459246276.98][HTST][INF] calling blocking teardown()
[1459246276.98][HTST][INF] teardown() finished
[1459246276.98][HTST][INF] {{result;failure}}
"""

        self.OUTOUT_CSTRING_TEST_CASE_COUNT_AND_NAME = """
[1467197417.13][SERI][TXD] {{__sync;3018cb93-f11c-417e-bf61-240c338dfec9}}
[1467197417.27][CONN][RXD] {{__sync;3018cb93-f11c-417e-bf61-240c338dfec9}}
[1467197417.27][CONN][INF] found SYNC in stream: {{__sync;3018cb93-f11c-417e-bf61-240c338dfec9}} it is #0 sent, queued...
[1467197417.27][HTST][INF] sync KV found, uuid=3018cb93-f11c-417e-bf61-240c338dfec9, timestamp=1467197417.272000
[1467197417.29][CONN][RXD] {{__version;1.1.0}}
[1467197417.29][CONN][INF] found KV pair in stream: {{__version;1.1.0}}, queued...
[1467197417.29][HTST][INF] DUT greentea-client version: 1.1.0
[1467197417.31][CONN][RXD] {{__timeout;5}}
[1467197417.31][CONN][INF] found KV pair in stream: {{__timeout;5}}, queued...
[1467197417.31][HTST][INF] setting timeout to: 5 sec
[1467197417.34][CONN][RXD] {{__host_test_name;default_auto}}
[1467197417.34][CONN][INF] found KV pair in stream: {{__host_test_name;default_auto}}, queued...
[1467197417.34][HTST][INF] host test class: '<class 'mbed_host_tests.host_tests.default_auto.DefaultAuto'>'
[1467197417.34][HTST][INF] host test setup() call...
[1467197417.34][HTST][INF] CALLBACKs updated
[1467197417.34][HTST][INF] host test detected: default_auto
[1467197417.36][CONN][RXD] {{__testcase_count;2}}
[1467197417.36][CONN][INF] found KV pair in stream: {{__testcase_count;2}}, queued...
[1467197417.39][CONN][RXD] >>> Running 2 test cases...
[1467197417.43][CONN][RXD] {{__testcase_name;C strings: strtok}}
[1467197417.43][CONN][INF] found KV pair in stream: {{__testcase_name;C strings: strtok}}, queued...
[1467197417.47][CONN][RXD] {{__testcase_name;C strings: strpbrk}}
[1467197417.47][CONN][INF] found KV pair in stream: {{__testcase_name;C strings: strpbrk}}, queued...
[1467197417.52][CONN][RXD] >>> Running case #1: 'C strings: strtok'...
[1467197417.56][CONN][RXD] {{__testcase_start;C strings: strtok}}
[1467197417.56][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: strtok}}, queued...
[1467197422.31][HTST][INF] test suite run finished after 5.00 sec...
[1467197422.31][CONN][INF] received special even '__host_test_finished' value='True', finishing
[1467197422.33][HTST][INF] CONN exited with code: 0
[1467197422.33][HTST][INF] No events in queue
[1467197422.33][HTST][INF] stopped consuming events
[1467197422.33][HTST][INF] host test result(): None
[1467197422.33][HTST][WRN] missing __exit event from DUT
[1467197422.33][HTST][ERR] missing __exit event from DUT and no result from host test, timeout...
[1467197422.33][HTST][INF] calling blocking teardown()
[1467197422.33][HTST][INF] teardown() finished
[1467197422.33][HTST][INF] {{result;timeout}}
"""

    def tearDown(self):
        pass

    def test_get_test_result(self):
        self.assertEqual(mbed_test_api.TEST_RESULT_OK, mbed_test_api.get_test_result(self.OUTPUT_SUCCESS))
        self.assertEqual(mbed_test_api.TEST_RESULT_FAIL, mbed_test_api.get_test_result(self.OUTPUT_FAILURE))
        self.assertEqual(mbed_test_api.TEST_RESULT_TIMEOUT, mbed_test_api.get_test_result(self.OUTPUT_TIMEOUT))
        self.assertEqual(mbed_test_api.TEST_RESULT_UNDEF, mbed_test_api.get_test_result(self.OUTPUT_UNDEF))

    def test_get_test_result_ok_len(self):
        r = mbed_test_api.get_testcase_utest(self.OUTOUT_CSTRING_TEST, 'C strings: %e %E float formatting')

        self.assertEqual(len(r), 6)
        self.assertIn("[1459246276.41][CONN][RXD] >>> Running case #7: 'C strings: %e %E float formatting'...", r)
        self.assertIn("[1459246276.46][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %e %E float formatting}}, queued...", r)
        self.assertIn("[1459246276.46][CONN][RXD] {{__testcase_start;C strings: %e %E float formatting}}", r)
        self.assertIn("[1459246276.52][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %e %E float formatting;1;0}}, queued...", r)
        self.assertIn("[1459246276.53][CONN][RXD] {{__testcase_finish;C strings: %e %E float formatting;1;0}}", r)
        self.assertIn("[1459246276.59][CONN][RXD] >>> 'C strings: %e %E float formatting': 1 passed, 0 failed", r)


    def test_get_test_result_fail_len(self):
        r = mbed_test_api.get_testcase_utest(self.OUTOUT_CSTRING_TEST, 'C strings: %f %f float formatting')

        self.assertEqual(len(r), 9)
        self.assertIn("[1459246275.88][CONN][RXD] >>> Running case #6: 'C strings: %f %f float formatting'...", r)
        self.assertIn("[1459246275.94][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %f %f float formatting}}, queued...", r)
        self.assertIn("[1459246275.94][CONN][RXD] {{__testcase_start;C strings: %f %f float formatting}}", r)
        self.assertIn("[1459246276.10][CONN][RXD] :57::FAIL: Expected '0.002000 0.924300 15.913200 791.773680 6208.200000 25719.495200 426815.982588 6429271.046000 42468024.930000 212006462.910000' Was '", r)
        self.assertIn("'", r)
        self.assertIn("[1459246276.18][CONN][RXD] >>> failure with reason 'Assertion Failed' during 'Case Handler'", r)
        self.assertIn("[1459246276.25][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %f %f float formatting;0;1}}, queued...", r)
        self.assertIn("[1459246276.25][CONN][RXD] {{__testcase_finish;C strings: %f %f float formatting;0;1}}", r)
        self.assertIn("[1459246276.34][CONN][RXD] >>> 'C strings: %f %f float formatting': 0 passed, 1 failed with reason 'Test Cases Failed'", r)

    def get_testcase_count_and_names(self):
        tc_count, tc_names = mbed_test_api.get_testcase_count_and_names(self.OUTOUT_CSTRING_TEST_CASE_COUNT_AND_NAME)

        self.assertEqual(tc_count, 2)
        self.assertIn('C strings: strtok', tc_names)
        self.assertIn('C strings: strpbrk', tc_names)

    def test_get_test_result_return_val(self):

        test_case_names = [
            'C strings: %e %E float formatting',
            'C strings: %g %g float formatting',
            'C strings: %i %d integer formatting',
            'C strings: %u %d integer formatting',
            'C strings: %x %E integer formatting',
            'C strings: strpbrk',
            'C strings: strtok'
        ]

        for test_case in test_case_names:
            r = mbed_test_api.get_testcase_utest(self.OUTOUT_CSTRING_TEST, test_case)
            self.assertEqual(len(r), 6)

        # This failing test case has different long lenght
        r = mbed_test_api.get_testcase_utest(self.OUTOUT_CSTRING_TEST, 'C strings: %f %f float formatting')
        self.assertEqual(len(r), 9)

    def test_get_testcase_summary_failures(self):
        r = mbed_test_api.get_testcase_summary("{{__testcase_summary;;}}")
        self.assertEqual(None, r)

        r = mbed_test_api.get_testcase_summary("{{__testcase_summary;-1;-2}}")
        self.assertEqual(None, r)

        r = mbed_test_api.get_testcase_summary("{{__testcase_summary;A;0}}")
        self.assertEqual(None, r)

    def test_get_testcase_summary_value_failures(self):
        r = mbed_test_api.get_testcase_summary("[1459246276.95][CONN][INF] found KV pair in stream: {{__testcase_summary;;}}")
        self.assertEqual(None, r)

        r = mbed_test_api.get_testcase_summary("[1459246276.95][CONN][INF] found KV pair in stream: {{__testcase_summary;-1;-2}}")
        self.assertEqual(None, r)

        r = mbed_test_api.get_testcase_summary("[1459246276.95][CONN][INF] found KV pair in stream: {{__testcase_summary;A;0}}")
        self.assertEqual(None, r)

    def test_get_testcase_summary_ok(self):

        r = mbed_test_api.get_testcase_summary("[1459246276.95][CONN][INF] found KV pair in stream: {{__testcase_summary;0;0}}")
        self.assertNotEqual(None, r)
        self.assertEqual((0, 0), r)

        r = mbed_test_api.get_testcase_summary(self.OUTOUT_CSTRING_TEST)
        self.assertNotEqual(None, r)
        self.assertEqual((7, 1), r)     # {{__testcase_summary;7;1}}

        r = mbed_test_api.get_testcase_summary(self.OUTPUT_SUCCESS)
        self.assertNotEqual(None, r)
        self.assertEqual((4, 0), r)     # {{__testcase_summary;4;0}}

    def test_get_testcase_result(self):
        r = mbed_test_api.get_testcase_result(self.OUTOUT_CSTRING_TEST)
        self.assertEqual(len(r), 8)

        test_case_names = [
            'C strings: %e %E float formatting',
            'C strings: %g %g float formatting',
            'C strings: %i %d integer formatting',
            'C strings: %u %d integer formatting',
            'C strings: %x %E integer formatting',
            'C strings: strpbrk',
            'C strings: strtok'
        ]

        for test_case in test_case_names:
            tc = r[test_case]
            # If datastructure is correct
            self.assertIn('utest_log', tc)
            self.assertIn('time_start', tc)
            self.assertIn('time_end', tc)
            self.assertIn('failed', tc)
            self.assertIn('result', tc)
            self.assertIn('passed', tc)
            self.assertIn('duration', tc)
            # values passed
            self.assertEqual(tc['passed'], 1)
            self.assertEqual(tc['failed'], 0)
            self.assertEqual(tc['result_text'], 'OK')

        # Failing test case
        tc = r['C strings: %f %f float formatting']
        self.assertEqual(tc['passed'], 0)
        self.assertEqual(tc['failed'], 1)
        self.assertEqual(tc['result_text'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
