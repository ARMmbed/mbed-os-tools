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

from conn_proxy_logger import HtrunLogger


class ConnectorPrimitive(object):

    def __init__(self, name):
        self.LAST_ERROR = None
        self.logger = HtrunLogger(name)

    def write_kv(self, key, value):
        """! Forms and sends Key-Value protocol message.
        @details On how to parse K-V sent from DUT see KiViBufferWalker::KIVI_REGEX
                 On how DUT sends K-V please see greentea_write_postamble() function in greentea-client
        @return Returns buffer with K-V message sent to DUT
        """
        # All Key-Value messages ends with newline character
        kv_buff = "{{%s;%s}}"% (key, value) + '\n'
        self.write(kv_buff)
        self.logger.prn_txd(kv_buff.rstrip())
        return kv_buff

    def read(self, count):
        raise NotImplementedError

    def write(self, payload, log=False):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def connected(self):
        raise NotImplementedError

    def error(self):
        raise NotImplementedError

    def finish(self):
        raise NotImplementedError
