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
from mbed_greentea import mbed_greentea_cli

class GreenteaFilteredTestList(unittest.TestCase):

    def setUp(self):
        self.ctest_test_list = {'test1': '\\build\\test1.bin',
                                'test2': '\\build\\test2.bin',
                                'test3': '\\build\\test3.bin',
                                'test4': '\\build\\test4.bin'}

    def tearDown(self):
        pass

    def test_skip_test(self):
        gt_opts = GtOptions(skip_test='test1,test2')
        filtered_ctest_test_list = mbed_greentea_cli.create_filtered_test_list(self.ctest_test_list, gt_opts)
        
        filtered_test_list = {'test3': '\\build\\test3.bin',
                              'test4': '\\build\\test4.bin'}
  
        self.assertEqual(filtered_test_list, filtered_ctest_test_list)

    def test_skip_test_invaild(self):
        gt_opts = GtOptions(skip_test='test1,testXY')
        filtered_ctest_test_list = mbed_greentea_cli.create_filtered_test_list(self.ctest_test_list, gt_opts)
        
        filtered_test_list = {'test2': '\\build\\test2.bin',
                              'test3': '\\build\\test3.bin',
                              'test4': '\\build\\test4.bin'}
  
        self.assertEqual(filtered_test_list, filtered_ctest_test_list)
    
    def test_test_by_names(self):
        gt_opts = GtOptions(test_by_names='test3')
        filtered_ctest_test_list = mbed_greentea_cli.create_filtered_test_list(self.ctest_test_list, gt_opts)
        
        filtered_test_list = {'test3': '\\build\\test3.bin'}
  
        self.assertEqual(filtered_test_list, filtered_ctest_test_list)
        
    def test_test_by_names_invalid(self):
        gt_opts = GtOptions(test_by_names='test3,testXY')
        filtered_ctest_test_list = mbed_greentea_cli.create_filtered_test_list(self.ctest_test_list, gt_opts)
        
        filtered_test_list = {'test3': '\\build\\test3.bin'}
  
        self.assertEqual(filtered_test_list, filtered_ctest_test_list)
        
    def test_test_by_names_and_skip_test(self):
        gt_opts = GtOptions(test_by_names='test1', skip_test='test1,test2')
        filtered_ctest_test_list = mbed_greentea_cli.create_filtered_test_list(self.ctest_test_list, gt_opts)
        
        filtered_test_list = {'test1': '\\build\\test1.bin'}
  
        self.assertEqual(filtered_test_list, filtered_ctest_test_list)
        
class GtOptions:
    def __init__(self,
                 test_by_names=None,
                 skip_test=None):

        self.test_by_names = test_by_names
        self.skip_test = skip_test
        
if __name__ == '__main__':
    unittest.main()
