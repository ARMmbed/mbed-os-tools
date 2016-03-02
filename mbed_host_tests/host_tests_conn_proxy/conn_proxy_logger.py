#!/usr/bin/env python
"""
mbed SDK
Copyright (c) 2011-2016 ARM Limited

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
    """! Yet another logger flavour """
    def __init__(self, prn_lock, name):
        self.__prn_lock = prn_lock
        self.__name = name

    def __prn_func(self, text, nl=True):
        """! Prints and flushes data to stdout """
        with self.__prn_lock:
            if nl and not text.endswith('\n'):
                text += '\n'
            sys.stdout.write(text)
            sys.stdout.flush()

    def __prn_log_human(self, level, text, timestamp=None):
        if not timestamp:
            timestamp = time()
        timestamp_str = strftime("%y-%m-%d %H:%M:%S", gmtime(timestamp))
        frac, whole = modf(timestamp)
        s = "[%s.%d][%s][%s] %s"% (timestamp_str, frac, self.__name, level, text)
        self.__prn_func(s, nl=True)

    def __prn_log(self, level, text, timestamp=None):
        if not timestamp:
            timestamp = time()
        s = "[%.2f][%s][%s] %s"% (timestamp, self.__name, level, text)
        self.__prn_func(s, nl=True)

    def prn_dbg(self, text, timestamp=None):
        self.__prn_log('DBG', text, timestamp)

    def prn_wrn(self, text, timestamp=None):
        self.__prn_log('WRN', text, timestamp)

    def prn_err(self, text, timestamp=None):
        self.__prn_log('ERR', text, timestamp)

    def prn_inf(self, text, timestamp=None):
        self.__prn_log('INF', text, timestamp)

    def prn_txt(self, text, timestamp=None):
        self.__prn_log('TXT', text, timestamp)

    def prn_txd(self, text, timestamp=None):
        self.__prn_log('TXD', text, timestamp)

    def prn_rxd(self, text, timestamp=None):
        self.__prn_log('RXD', text, timestamp)
