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

from conn_primitive import ConnectorPrimitive


class RemoteConnectorPrimitive(ConnectorPrimitive):
    def __init__(self, name, port, baudrate, config):
        ConnectorPrimitive.__init__(self, name)
        self.port = port
        self.baudrate = int(baudrate)
        self.timeout = 0
        self.config = config
        self.target_id = self.config.get('target_id', None)

    def __remote_reset(self):
        pass

    def __remote_flashing(self):
        pass

    def read(self, count):
        pass

    def write(self, payload, log=False):
        pass

    def flush(self):
        pass

    def connected(self):
        pass

    def error(self):
        pass

    def finish(self):
        pass
