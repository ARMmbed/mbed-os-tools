#!/usr/bin/env python
"""
mbed SDK
Copyright (c) 2017 ARM Limited

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
from mock import patch

from mbed_greentea.mbed_report_api import exporter_html, \
    exporter_memory_metrics_csv, exporter_testcase_junit, \
    exporter_testcase_text, exporter_text, exporter_json


class ReportEmitting(unittest.TestCase):


    report_fns =  [exporter_html, exporter_memory_metrics_csv,
                   exporter_testcase_junit, exporter_testcase_text,
                   exporter_text, exporter_json]
    def test_report_zero_tests(self):
        test_data = {}
        for report_fn in self.report_fns:
            report_fn(test_data)

    def test_report_zero_testcases(self):
        test_data = {
            'k64f-gcc_arm': {
                'garbage_test_suite' :{
                    'single_test_result': 'NOT_RAN',
                    'elapsed_time': 0.0,
                    'build_path': 'N/A',
                    'build_path_abs': 'N/A',
                    'copy_method': 'N/A',
                    'image_path': 'N/A',
                    'single_test_output': 'N/A',
                    'platform_name': 'k64f',
                    'test_bin_name': 'N/A',
                    'testcase_result': {},
                }
            }
        }
        for report_fn in self.report_fns:
            report_fn(test_data)
