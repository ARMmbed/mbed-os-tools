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
import logging
from time import time


class HtrunLogger(object):
    """! Yet another logger flavour """
    def __init__(self, name):
        logging.basicConfig(stream=sys.stdout,format='[%(created).2f][%(name)s][%(logger_level)s] %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger(name)

    def prn_dbg(self, text, timestamp=None):
        self.logger.debug(text, extra={'logger_level': 'DBG'})

    def prn_wrn(self, text, timestamp=None):
        self.logger.debug(text, extra={'logger_level': 'WRN'})

    def prn_err(self, text, timestamp=None):
        self.logger.debug(text, extra={'logger_level': 'ERR'})

    def prn_inf(self, text, timestamp=None):
        self.logger.debug(text, extra={'logger_level': 'INF'})

    def prn_txt(self, text, timestamp=None):
        self.logger.debug(text, extra={'logger_level': 'TXT'})

    def prn_txd(self, text, timestamp=None):
        self.logger.debug(text, extra={'logger_level': 'TXD'})

    def prn_rxd(self, text, timestamp=None):
        self.logger.debug(text, extra={'logger_level': 'RXD'})
