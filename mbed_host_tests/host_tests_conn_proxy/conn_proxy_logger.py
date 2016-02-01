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


import sys
from time import time


class HtrunLogger(object):
    def __init__(self, prn_lock):
        self.prn_lock = prn_lock

    def _prn_func(self, text, nl=True):
        with self.prn_lock:
            if nl and not text.endswith('\n'):
                text += '\n'
            sys.stdout.write(text)

    def _prn_log(self, level, text, timestamp=None):
        if not timestamp:
            timestamp = time()
        s = "[%.2f][%s] %s"% (timestamp, level, text)
        self._prn_func(s, nl=True)

    def prn_dbg(self, text, timestamp=None):
        self._prn_log('DBG', text, timestamp)

    def prn_wrn(self, text, timestamp=None):
        self._prn_log('WRN', text, timestamp)

    def prn_err(self, text, timestamp=None):
        self._prn_log('ERR', text, timestamp)

    def prn_inf(self, text, timestamp=None):
        self._prn_log('INF', text, timestamp)
