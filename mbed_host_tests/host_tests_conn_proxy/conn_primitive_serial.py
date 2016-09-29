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


import time
from serial import Serial, SerialException
from mbed_host_tests import host_tests_plugins
from mbed_host_tests.host_tests_plugins.host_test_plugins import HostTestPluginBase
from conn_primitive import ConnectorPrimitive, ConnectorPrimitiveException


class SerialConnectorPrimitive(ConnectorPrimitive):
    def __init__(self, name, port, baudrate, config):
        ConnectorPrimitive.__init__(self, name)
        self.port = port
        self.baudrate = int(baudrate)
        self.read_timeout = 0.01  # 10 milli sec
        self.write_timeout = 5
        self.config = config
        self.target_id = self.config.get('target_id', None)
        self.polling_timeout = config.get('polling_timeout', 60)
        self.forced_reset_timeout = config.get('forced_reset_timeout', 1)
        self.skip_reset = config.get('skip_reset', False)
        self.serial = None

        # Check if serial port for given target_id changed
        # If it does we will use new port to open connections and make sure reset plugin
        # later can reuse opened already serial port
        #
        # Note: This listener opens serial port and keeps connection so reset plugin uses
        # serial port object not serial port name!
        serial_port = HostTestPluginBase().check_serial_port_ready(self.port, target_id=self.target_id, timeout=self.polling_timeout)
        if serial_port is None:
            raise ConnectorPrimitiveException("Serial port not ready!")

        if serial_port != self.port:
            # Serial port changed for given targetID
            self.logger.prn_inf("serial port changed from '%s to '%s')"% (self.port, serial_port))
            self.port = serial_port

        startTime = time.time()
        self.logger.prn_inf("serial(port=%s, baudrate=%d, read_timeout=%s, write_timeout=%d)"% (self.port, self.baudrate, self.read_timeout, self.write_timeout))
        while time.time() - startTime < self.polling_timeout:
            try:
                # TIMEOUT: While creating Serial object timeout is delibrately passed as 0. Because blocking in Serial.read
                # impacts thread and mutliprocess functioning in Python. Hence, instead in self.read() s delay (sleep()) is
                # inserted to let serial buffer collect data and avoid spinning on non blocking read().
                self.serial = Serial(self.port, baudrate=self.baudrate, timeout=0, write_timeout=self.write_timeout)
            except SerialException as e:
                self.serial = None
                self.LAST_ERROR = "connection lost, serial.Serial(%s, %d, %d, %d): %s"% (self.port,
                    self.baudrate,
                    self.read_timeout,
                    self.write_timeout,
                    str(e))
                self.logger.prn_err(str(e))
                self.logger.prn_err("Retry after 1 sec until %s seconds" % self.polling_timeout)
            else:
                if not self.skip_reset:
                    self.reset_dev_via_serial(delay=self.forced_reset_timeout)
                break
            time.sleep(1)

    def reset_dev_via_serial(self, delay=1):
        """! Reset device using selected method, calls one of the reset plugins """
        reset_type = self.config.get('reset_type', 'default')
        if not reset_type:
            reset_type = 'default'
        disk = self.config.get('disk', None)

        self.logger.prn_inf("reset device using '%s' plugin..."% reset_type)
        result = host_tests_plugins.call_plugin('ResetMethod',
            reset_type,
            serial=self.serial,
            disk=disk,
            target_id=self.target_id)
        # Post-reset sleep
        if delay:
            self.logger.prn_inf("waiting %.2f sec after reset"% delay)
            time.sleep(delay)
        self.logger.prn_inf("wait for it...")
        return result

    def read(self, count):
        """! Read data from serial port RX buffer """
        # TIMEOUT: Since read is called in a loop, wait for self.timeout period before calling serial.read(). See
        # comment on serial.Serial() call above about timeout.
        time.sleep(self.timeout)
        c = str()
        try:
            if self.serial:
                c = self.serial.read(count)
        except SerialException as e:
            self.serial = None
            self.LAST_ERROR = "connection lost, serial.read(%d): %s"% (count, str(e))
            self.logger.prn_err(str(e))
        return c

    def write(self, payload, log=False):
        """! Write data to serial port TX buffer """
        try:
            if self.serial:
                self.serial.write(payload)
                if log:
                    self.logger.prn_txd(payload)
                return True
        except SerialException as e:
            self.serial = None
            self.LAST_ERROR = "connection lost, serial.write(%d bytes): %s"% (len(payload), str(e))
            self.logger.prn_err(str(e))
        return False

    def flush(self):
        if self.serial:
            self.serial.flush()

    def connected(self):
        return bool(self.serial)

    def finish(self):
        if self.serial:
            self.serial.close()

    def __del__(self):
        self.finish()
