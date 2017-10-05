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

from mbed_host_tests import DEFAULT_BAUD_RATE
from mbed_host_tests.host_tests_conn_proxy.conn_primitive import ConnectorPrimitive


class RemoteConnectorPrimitive(ConnectorPrimitive):
    def __init__(self, name, config):
        ConnectorPrimitive.__init__(self, name)
        self.config = config
        self.target_id = self.config.get('target_id', None)
        self.grm_host = config.get('grm_host', None)
        self.grm_port = int(config.get('grm_port', 8000))
        self.grm_module = config.get('grm_module', 'unknown')
        self.platform_name = config.get('platform_name', None)
        self.baudrate = config.get('baudrate', DEFAULT_BAUD_RATE)
        self.image_path = config.get('image_path', None)
        self.polling_timeout = int(config.get('polling_timeout', 60))
        self.allocate_requirements = { "platform_name": self.platform_name }

        if self.config["tags"]:
            self.allocate_requirements["tags"] = {}
            for tag in config["tags"].split(','):
                self.allocate_requirements["tags"][tag] = True

        # Global Resource Mgr tool-kit
        self.remote_module = None
        self.selected_resource = None
        self.client = None

        # Initialize remote resource manager
        self.__remote_init()

    def __remote_init(self):
        """! Initialize DUT using GRM APIs """

        # We want to load global resource manager module by name from command line (switch --grm)
        try:
            self.remote_module = __import__(self.grm_module)
        except ImportError as e:
            self.logger.prn_err("unable to load global resource manager '%s' module!"% self.grm_module)
            self.remote_module = None
            return False

        self.logger.prn_inf("remote resources initialization: remote(host=%s, port=%s)"% (self.grm_host, self.grm_port))

        # Connect to remote global resource manager
        self.client = self.remote_module.create(host=self.grm_host, port=self.grm_port)

        # First get the resources
        resources = self.client.get_resources()
        self.logger.prn_inf("remote resources count: %d" % len(resources))

        # Query for available resource
        # Automatic selection and allocation of a resource
        try:
            self.selected_resource = self.client.allocate(self.allocate_requirements)

        except self.remote_module.resources.ResourceError as e:
            self.logger.prn_err("can't allocate resource: '%s', reason: %s"% (self.platform_name, str(e)))
            return False

        # Remote DUT connection, flashing and reset...
        try:
            self.__remote_flashing(self.image_path, forceflash=True)
            self.__remote_connect(baudrate=self.baudrate)
            self.__remote_reset()
        except Exception as e:
            self.logger.prn_err(str(e))
            return False
        return True

    def __remote_connect(self, baudrate=DEFAULT_BAUD_RATE, buffer_size=6):
        """! Open remote connection to DUT """
        self.logger.prn_inf("opening connection to platform at baudrate='%s, bufferSize=%d'"% (baudrate, buffer_size))
        if not self.selected_resource:
            raise Exception("remote resource not exists!")
        try:
            serial_parameters = self.remote_module.SerialParameters(lineMode=False, baudrate=baudrate, bufferSize=buffer_size)
            self.selected_resource.openConnection(parameters=serial_parameters)
        except self.remote_module.resources.ResourceError as e:
            self.logger.prn_inf("openConnection() failed")
            raise e

    def __remote_disconnect(self):
        if not self.selected_resource:
            raise Exception("remote resource not exists!")
        if self.selected_resource.is_connected:
            self.selected_resource.closeConnection()

    def __remote_reset(self):
        """! Use GRM remote API to reset DUT """
        self.logger.prn_inf("remote resources reset...")
        if not self.selected_resource:
            raise Exception("remote resource not exists!")
        if not self.selected_resource.reset():
            raise Exception("remote resources reset failed!")

    def __remote_flashing(self, filename, forceflash=False):
        """! Use GRM remote API to flash DUT """
        self.logger.prn_inf("remote resources flashing with '%s'..."% filename)
        if not self.selected_resource:
            raise Exception("remote resource not exists!")
        if not self.selected_resource.flash(filename, forceflash=forceflash):
            raise Exception("remote resources flashing failed!")

    def read(self, count):
        """! Read 'count' bytes of data from DUT """
        if not self.selected_resource:
            raise Exception("remote resource not exists!")
        date = str()
        try:
            data = self.selected_resource.read(count)
        except self.remote_module.resources.ResourceError as e:
            self.logger.prn_err("RemoteConnectorPrimitive.read(%d): %s"% (count, str(e)))
        return data

    def write(self, payload, log=False):
        """! Write 'payload' to DUT """
        if self.selected_resource:
            self.selected_resource.write(payload)
            if log:
                self.logger.prn_txd(payload)
        return True

    def flush(self):
        pass

    def connected(self):
        return all([self.remote_module,
            self.selected_resource,
            self.selected_resource.is_connected])

    def finish(self):
        # Finally once we're done with the resource
        # we disconnect and release the allocation
        if self.selected_resource:
            try:
                if self.selected_resource.is_connected:
                    self.selected_resource.closeConnection()
                if self.selected_resource.is_allocated:
                    self.selected_resource.release()
                    self.selected_resource = None
            except self.remote_module.resources.ResourceError as e:
                self.logger.prn_err("RemoteConnectorPrimitive.finish() failed, reason: " + str(e))

    def __del__(self):
        self.finish()
