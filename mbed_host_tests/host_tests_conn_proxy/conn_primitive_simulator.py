#!/usr/bin/env python
"""
mbed SDK
Copyright (c) 2011-2018 ARM Limited

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
import telnetlib
import socket
from .conn_primitive import ConnectorPrimitive, ConnectorPrimitiveException


class SimulatorConnectorPrimitive(ConnectorPrimitive):
    def __init__(self, name, config):
        ConnectorPrimitive.__init__(self, name)
        self.config          = config
        self.srm_config      = config.get('srm_config', None)
        self.srm_module      = config.get('srm_module', 'unknown')
        self.platform_name   = config.get('platform_name', None)
        self.image_path      = config.get('image_path', None)
        self.polling_timeout = int(config.get('polling_timeout', 60))

        # Simulator Resource Mgr tool-kit
        self.simulator_module = None
        self.resource = None

        # Initialize simulator
        if self.__simulator_init():
        
            # Simulator Launch load and run, equivalent to DUT connection, flashing and reset...
            self.__simulator_launch()
            self.__simulator_load(self.image_path)
            self.__simulator_run()


    def __simulator_init(self):
        """! Initialize models using SRM APIs """
        self.logger.prn_inf("Initializing Simulator...")
        # We want to load simulator resource manager module by name from command line (switch --srm)
        try:
            self.simulator_module = __import__(self.srm_module)
        except ImportError as e:
            self.logger.prn_err("unable to load simulator resource manager '%s' module!"% self.srm_module)
            self.simulator_module = None
            self.logger.prn_err("Importing failed : %s" % str(e))
            raise ConnectorPrimitiveException("Importing failed : %s" % str(e))
        try:
            self.resource = self.simulator_module.create(self.platform_name,self.srm_config,self.logger)
            if self.__resource_allocated():
                pass
        except self.simulator_module.SimulatorError as e:
            self.logger.prn_err("module %s, create() failed: %s"% (self.srm_module,str(e)))
            raise ConnectorPrimitiveException("Simulator Initializing failed as throw SimulatorError!")
            
        return True

    def __simulator_launch(self):
        """! launch the simulator"""
        self.logger.prn_inf("Launching Simulator...")
        try:
            if not self.resource.start_simulator():
                raise ConnectorPrimitiveException("Simulator running failed, run_simulator() return False!")
        except self.simulator_module.SimulatorError as e:
            self.logger.prn_err("start_simulator() failed: %s"% str(e))
            raise ConnectorPrimitiveException("Simulator launching failed as throw SimulatorError!")
            
    def __simulator_run(self):
        """! Use SRM API to run the simulator, this is functionally equivalent to reset DUT """
        self.logger.prn_inf("Running Simulator...")
        try:
            if not self.resource.run_simulator():
                raise ConnectorPrimitiveException("Simulator running failed, run_simulator() return False!")
        except self.simulator_module.SimulatorError as e:
            self.logger.prn_err("run_simulator() failed: %s"% str(e))
            raise ConnectorPrimitiveException("Simulator running failed as throw SimulatorError!")

    def __simulator_load(self, filename):
        """! Use SRM API to load image to simulator, this is functional equivalent to flashing DUT"""
        self.logger.prn_inf("loading Simulator with image '%s'..."% filename)
        try:
            if not self.resource.load_simulator(filename):
                raise ConnectorPrimitiveException("Simulator loading failed, load_simulator() return False!")
        except self.simulator_module.SimulatorError as e:
            self.logger.prn_err("run_simulator() failed: %s"% str(e))
            raise ConnectorPrimitiveException("Simulator loading failed as throw SimulatorError!")

    def __resource_allocated(self):
        """! Check whether Simulator resource been allocated
           @return True or throw an exception 
        """
        if self.resource:
            return True
        else:
            self.logger.prn_err("Simulator resource not available!")
            return False
        
    def read(self, count):
        """! Read data from DUT, count is not used for simulator"""
        date = str()
        if self.__resource_allocated():
            try:
                data = self.resource.read()
            except self.simulator_module.SimulatorError as e:
                self.logger.prn_err("SimulatorConnectorPrimitive.read() failed: %s"% str(e))
            else:
                return data
        else:
            return False
    def write(self, payload, log=False):
        """! Write 'payload' to DUT"""
        if self.__resource_allocated():
            if log:
                self.logger.prn_txd(payload)       
            try:
                self.resource.write(payload)
            except self.simulator_module.SimulatorError as e:
                self.logger.prn_err("SimulatorConnectorPrimitive.write() failed: %s"% str(e))
            else:
                return True
        else:
            return False

    def flush(self):
        """! flush not supported in simulator_module"""
        pass

    def connected(self):
        """! return whether simulator is connected """
        if self.__resource_allocated():
            return self.resource.is_simulator_alive
        else:
            return False

    def finish(self):
        """! shutdown the simulator and release the allocation """
        if self.__resource_allocated():
            try:
                self.resource.shutdown_simulator()
                self.resource = None
            except self.simulator_module.SimulatorError as e:
                self.logger.prn_err("SimulatorConnectorPrimitive.finish() failed: %s"% str(e))

    def reset(self):
        self.__simulator_run()

    def __del__(self):
        self.finish()
