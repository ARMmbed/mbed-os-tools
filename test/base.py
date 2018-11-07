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
import os
import errno
import logging
import re
import json
from mock import patch, MagicMock
from copy import deepcopy
from six import StringIO

import mbed_tools.detect.main as cli


try:
    basestring
except NameError:
    # Python 3
    basestring = str

class CLIComands(unittest.TestCase):
    """ Test the CLI
    """

    def setUp(self):
        self._stdout = patch('sys.stdout', new_callable=StringIO)
        self.stdout = self._stdout.start()
        self.mbeds = MagicMock()
        self.args = MagicMock()
        self.mbeds.list_mbeds.return_value = [
            {'platform_name': 'foo', 'platform_name_unique': 'foo[0]',
             'mount_point': 'a mount point', 'serial_port': 'a serial port',
             'target_id': 'DEADBEEF', 'daplink_version': 'v12345'
            }
        ]

    def tearDown(self):
        self._stdout.stop()

    def test_print_table(self):
        cli.print_table(self.mbeds, self.args)
        for d in self.mbeds.list_mbeds.return_value:
            for v in d.values():
                self.assertIn(v, self.stdout.getvalue())

    def test_print_simple(self):
        cli.print_simple(self.mbeds, self.args)
        for d in self.mbeds.list_mbeds.return_value:
            for v in d.values():
                self.assertIn(v, self.stdout.getvalue())

    def test_mbeds_as_json(self):
        cli.mbeds_as_json(self.mbeds, self.args)
        self.assertEqual(self.mbeds.list_mbeds.return_value,
                         json.loads(self.stdout.getvalue()))

    def test_json_by_target_id(self):
        cli.json_by_target_id(self.mbeds, self.args)
        out_dict = json.loads(self.stdout.getvalue())
        for d in out_dict.values():
            self.assertIn(d, self.mbeds.list_mbeds.return_value)

    def test_json_platforms(self):
        cli.json_platforms(self.mbeds, self.args)
        platform_names = [d['platform_name'] for d
                          in self.mbeds.list_mbeds.return_value]
        for name in json.loads(self.stdout.getvalue()):
            self.assertIn(name, platform_names)

    def test_json_platforms_ext(self):
        cli.json_platforms_ext(self.mbeds, self.args)
        platform_names = [d['platform_name'] for d
                          in self.mbeds.list_mbeds.return_value]
        for name in json.loads(self.stdout.getvalue()).keys():
            self.assertIn(name, platform_names)

    def test_list_platform(self):
        self.mbeds.list_manufacture_ids.return_value ="""
        foo
        bar
        baz
        """
        cli.list_platforms(self.mbeds, self.args)
        self.assertIn(self.mbeds.list_manufacture_ids.return_value,
                      self.stdout.getvalue())

class CLIParser(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

