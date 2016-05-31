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

import re
import uuid
from time import time, sleep
from Queue import Empty as QueueEmpty   # Queue here refers to the module, not a class
from serial import Serial, SerialException
from mbed_host_tests import host_tests_plugins
from mbed_host_tests.host_tests_plugins.host_test_plugins import HostTestPluginBase
from conn_proxy_logger import HtrunLogger


class SerialConnectorPrimitive(object):
    def __init__(self, port, baudrate, prn_lock, config):
        self.port = port
        self.baudrate = int(baudrate)
        self.timeout = 0
        self.prn_lock = prn_lock
        self.config = config
        self.logger = HtrunLogger(prn_lock, 'SERI')
        self.LAST_ERROR = None
        self.target_id = self.config.get('target_id', None)
        self.serial_pooling = config.get('serial_pooling', 60)

        # Values used to call serial port listener...
        self.logger.prn_inf("serial(port=%s, baudrate=%d, timeout=%s)"% (self.port, self.baudrate, self.timeout))

        # Check if serial port for given target_id changed
        # If it does we will use new port to open connections and make sure reset plugin
        # later can reuse opened already serial port
        #
        # Note: This listener opens serial port and keeps connection so reset plugin uses
        # serial port object not serial port name!
        _, serial_port = HostTestPluginBase().check_serial_port_ready(self.port, target_id=self.target_id, timeout=self.serial_pooling)
        if serial_port != self.port:
            # Serial port changed for given targetID
            self.logger.prn_inf("serial port changed from '%s to '%s')"% (self.port, serial_port))
            self.port = serial_port

        try:
            self.serial = Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)
        except SerialException as e:
            self.serial = None
            self.LAST_ERROR = "connection lost, serial.Serial(%s. %d, %d): %s"% (self.port,
                self.baudrate,
                self.timeout,
                str(e))
            self.logger.prn_err(str(e))
        else:
            self.reset_dev_via_serial()

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
        self.logger.prn_inf("wait for it...")
        sleep(delay)
        return result

    def read(self, count):
        """! Read data from serial port RX buffer """
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
        except SerialException as e:
            self.serial = None
            self.LAST_ERROR = "connection lost, serial.write(%d bytes): %s"% (len(payload), str(e))
            self.logger.prn_err(str(e))
        return payload

    def write_kv(self, key, value):
        kv_buff = "{{%s;%s}}\n"% (key, value)
        self.write(kv_buff)
        self.logger.prn_txd(kv_buff)
        return kv_buff

    def flush(self):
        if self.serial:
            self.serial.flush()

    def connected(self):
        return bool(self.serial)

    def error(self):
        return self.LAST_ERROR

    def finish(self):
        if self.serial:
            self.serial.close()


class KiViBufferWalker():
    """! Simple auxiliary class used to walk through a buffer and search for KV tokens """
    def __init__(self):
        self.KIVI_REGEX = r"\{\{([\w\d_-]+);([^\}]+)\}\}"
        self.buff = str()
        self.buff_idx = 0
        self.re_kv = re.compile(self.KIVI_REGEX)

    def append(self, payload):
        """! Append stream buffer with payload """
        self.buff += payload

    def search(self):
        """! Check if there is a KV value in buffer """
        return self.re_kv.search(self.buff[self.buff_idx:])

    def get_kv(self):
        m = self.re_kv.search(self.buff[self.buff_idx:])
        if m:
            (key, value) = m.groups()
            kv_str = m.group(0)
            self.buff_idx = self.buff.find(kv_str, self.buff_idx) + len(kv_str)
        return (key, value, time())


def conn_process(event_queue, dut_event_queue, prn_lock, config):

    logger = HtrunLogger(prn_lock, 'CONN')
    logger.prn_inf("starting serial connection process...")

    port = config.get('port')
    baudrate = config.get('baudrate')
    serial_pooling = int(config.get('serial_pooling', 60))

    # Notify event queue we will wait additional time for serial port to be ready
    logger.prn_inf("notify event queue about extra %d sec timeout for serial port pooling"%serial_pooling)
    event_queue.put(('__timeout', serial_pooling, time()))

    logger.prn_inf("initializing serial port listener... ")
    connector = SerialConnectorPrimitive(port,
        baudrate,
        prn_lock,
        config=config)

    kv_buffer = KiViBufferWalker()
    sync_uuid = str(uuid.uuid4())

    # We will ignore all kv pairs before we get sync back
    sync_uuid_discovered = False

    # Some RXD data buffering so we can show more text per log line
    print_data = str()

    # Handshake, we will send {{sync;UUID}} preamble and wait for mirrored reply
    logger.prn_inf("sending preamble '%s'..."% sync_uuid)
    connector.write("mbed" * 10, log=True)
    connector.write_kv('__sync', sync_uuid)

    while True:

        # Check if connection is lost to serial
        if not connector.connected():
            error_msg = connector.error()
            connector.finish()
            event_queue.put(('__notify_conn_lost', error_msg, time()))
            break

        # Send data to DUT
        try:
            (key, value, _) = dut_event_queue.get(timeout=1)
        except QueueEmpty:
            pass # Check if target sent something
        else:
            # Return if state machine in host_test_default has finished to end process
            if key == '__host_test_finished' and value == True:
                logger.prn_inf("received special even '%s' value='%s', finishing"% (key, value))
                connector.finish()
                return 0
            connector.write_kv(key, value)

        data = connector.read(2048)
        if data:

            # We want to print RXD data with nice line division in log
            print_data += data
            print_data_lines = print_data.split('\n')
            if print_data_lines:
                if data.endswith('\n'):
                    for line in print_data_lines:
                        if line:
                            logger.prn_rxd(line)
                            event_queue.put(('__rxd_line', line, time()))
                    print_data = str()
                else:
                    for line in print_data_lines[:-1]:
                        if line:
                            logger.prn_rxd(line)
                            event_queue.put(('__rxd_line', line, time()))
                    print_data = print_data_lines[-1]

            # Stream data stream KV parsing
            kv_buffer.append(data)
            while kv_buffer.search():
                key, value, timestamp = kv_buffer.get_kv()

                if sync_uuid_discovered:
                    event_queue.put((key, value, timestamp))
                    logger.prn_inf("found KV pair in stream: {{%s;%s}}, queued..."% (key, value))
                else:
                    if key == '__sync':
                        if value == sync_uuid:
                            sync_uuid_discovered = True
                            event_queue.put((key, value, time()))
                            logger.prn_inf("found SYNC in stream: {{%s;%s}}, queued..."% (key, value))
                        else:
                            logger.prn_err("found faulty SYNC in stream: {{%s;%s}}, ignored..."% (key, value))
                    else:
                        logger.prn_wrn("found KV pair in stream: {{%s;%s}}, ignoring..."% (key, value))

    return 0
