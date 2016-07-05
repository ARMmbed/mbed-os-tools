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
from mbed_host_tests.host_tests_logger import HtrunLogger


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


class SerialConnectorPrimitive(ConnectorPrimitive):
    def __init__(self, name, port, baudrate, config):
        ConnectorPrimitive.__init__(self, name)
        self.port = port
        self.baudrate = int(baudrate)
        self.timeout = 0
        self.config = config
        self.target_id = self.config.get('target_id', None)
        self.serial_pooling = config.get('serial_pooling', 60)
        self.forced_reset_timeout = config.get('forced_reset_timeout', 1)

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
            self.reset_dev_via_serial(delay=self.forced_reset_timeout)

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
            sleep(delay)
        self.logger.prn_inf("wait for it...")
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
        self.KIVI_REGEX = r"\{\{([\w\d_-]+);([^\}]+)\}\}\n"
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


def conn_process(event_queue, dut_event_queue, config):

    logger = HtrunLogger('CONN')
    logger.prn_inf("starting serial connection process...")

    port = config.get('port')
    baudrate = config.get('baudrate')
    serial_pooling = int(config.get('serial_pooling', 60))
    sync_behavior = int(config.get('sync_behavior', 1))
    sync_timeout = config.get('sync_timeout', 1.0)

    # Notify event queue we will wait additional time for serial port to be ready
    logger.prn_inf("notify event queue about extra %d sec timeout for serial port pooling"%serial_pooling)
    event_queue.put(('__timeout', serial_pooling, time()))

    logger.prn_inf("initializing serial port listener... ")
    connector = SerialConnectorPrimitive(
        'SERI',
        port,
        baudrate,
        config=config)

    kv_buffer = KiViBufferWalker()

    # List of all sent to target UUIDs (if multiple found)
    sync_uuid_list = []

    # We will ignore all kv pairs before we get sync back
    sync_uuid_discovered = False

    # Some RXD data buffering so we can show more text per log line
    print_data = str()

    def __send_sync(timeout=None):
        sync_uuid = str(uuid.uuid4())
        # Handshake, we will send {{sync;UUID}} preamble and wait for mirrored reply
        if timeout:
            logger.prn_inf("resending new preamble '%s' after %0.2f sec"% (sync_uuid, timeout))
        else:
            logger.prn_inf("sending preamble '%s'"% sync_uuid)
        connector.write_kv('__sync', sync_uuid)
        return sync_uuid

    # Send simple string to device to 'wake up' greentea-client k-v parser
    connector.write("mbed" * 10, log=True)

    # Sync packet management allows us to manipulate the way htrun sends __sync packet(s)
    # With current settings we can force on htrun to send __sync packets in this manner:
    #
    # * --sync=0        - No sync packets will be sent to target platform
    # * --sync=-10      - __sync packets will be sent unless we will reach
    #                     timeout or proper response is sent from target platform
    # * --sync=N        - Send up to N __sync packets to target platform. Response
    #                     is sent unless we get response from target platform or
    #                     timeout occur

    if sync_behavior > 0:
        # Sending up to 'n' __sync packets
        logger.prn_inf("sending up to %s __sync packets (specified with --sync=%s)"% (sync_behavior, sync_behavior))
        sync_uuid_list.append(__send_sync())
        sync_behavior -= 1
    elif sync_behavior == 0:
        # No __sync packets
        logger.prn_wrn("skipping __sync packet (specified with --sync=%s)"% sync_behavior)
    else:
        # Send __sync until we go reply
        logger.prn_inf("sending multiple __sync packets (specified with --sync=%s)"% sync_behavior)
        sync_uuid_list.append(__send_sync())
        sync_behavior -= 1

    loop_timer = time()
    while True:

        # Check if connection is lost to serial
        if not connector.connected():
            error_msg = connector.error()
            connector.finish()
            event_queue.put(('__notify_conn_lost', error_msg, time()))
            break

        # Send data to DUT
        try:
            (key, value, _) = dut_event_queue.get(block=False)
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
                        if value in sync_uuid_list:
                            sync_uuid_discovered = True
                            event_queue.put((key, value, time()))
                            idx = sync_uuid_list.index(value)
                            logger.prn_inf("found SYNC in stream: {{%s;%s}} it is #%d sent, queued..."% (key, value, idx))
                        else:
                            logger.prn_err("found faulty SYNC in stream: {{%s;%s}}, ignored..."% (key, value))
                    else:
                        logger.prn_wrn("found KV pair in stream: {{%s;%s}}, ignoring..."% (key, value))

        if not sync_uuid_discovered:
            # Resending __sync after 'sync_timeout' secs (default 1 sec)
            # to target platform. If 'sync_behavior' counter is != 0 we
            # will continue to send __sync packets to target platform.
            # If we specify 'sync_behavior' < 0 we will send 'forever'
            # (or until we get reply)

            if sync_behavior != 0:
                time_to_sync_again = time() - loop_timer
                if time_to_sync_again > sync_timeout:
                    sync_uuid_list.append(__send_sync(timeout=time_to_sync_again))
                    sync_behavior -= 1
                    loop_timer = time()

    return 0
