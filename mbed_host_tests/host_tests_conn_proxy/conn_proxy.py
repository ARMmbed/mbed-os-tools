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

import re
import sys
import uuid
from serial import Serial, SerialException
from time import sleep, time
from conn_proxy_logger import HtrunLogger


class SerialConnectorPrimitive(object):
    def __init__(self, port, baudrate, prn_lock, config):
        #ConnectorPrimitive.__init__(self)
        self.prn_lock = prn_lock
        self.config = config
        self.logger = HtrunLogger(prn_lock)
        program_cycle_s = int(self.config['program_cycle_s']) if 'program_cycle_s' in self.config else 4

        self.logger.prn_inf("Serial port=%s baudrate=%s program_cycle_s=%s"% (str(port), (baudrate), (program_cycle_s)))
        try:
            self.serial = Serial(port, baudrate=baudrate, timeout=0)
        except SerialException as e:
            self.logger.prn_err(str(e))
            self.serial = None
        self.send_break()
        sleep(program_cycle_s)

    def send_break(self, delay=0.5):
        self.logger.prn_inf("reset device (send_break(%.2f sec))"% delay)
        if self.serial:
            self.serial.send_break(delay)
        
    def read(self, count):
        c = ''
        try:
            if self.serial:
                c = self.serial.read(count)
        except SerialException as e:
            self.serial = None
            self.logger.prn_err(str(e))
        return c

    def write(self, payload):
        try:
            if self.serial:
                self.serial.write(payload)
        except SerialException as e:
            self.serial = None
            self.logger.prn_err(str(e))

    def write_kv(self, key, value):
        kv_buff = "{{%s;%s}}\n"% (key, value)
        self.write(kv_buff)

    def flush(self):
        if self.serial:
            self.serial.flush()

    def finish(self):
        if self.serial:
            self.serial.close()

            
def conn_process(event_queue, prn_lock, config):

    port = config['port'] if 'port' in config else None
    baudrate = config['baudrate'] if 'baudrate' in config else None
    logger = HtrunLogger(prn_lock)

    logger.prn_inf("Starting process... ")
    
    connector = SerialConnectorPrimitive(port,
        baudrate,
        prn_lock,
        config=config)

    kv = re.compile(r"\{\{([\w\d_-]+);([^\}]+)\}\}")
    buff = ''
    buff_idx = 0
    sync_uuid = str(uuid.uuid4())
    
    # We will ignore all kv pairs before we get sync back
    sync_uuid_discovered = False

    logger.prn_inf("Sending preamble...")

    connector.write_kv('sync', sync_uuid)

    while True:
        data = connector.read(512)
        buff += data

        m = kv.search(buff[buff_idx:])
        if m:
            (key, value) = m.groups()
            kv_str = m.group(0)
            buff_idx = buff.find(kv_str, buff_idx) + len(kv_str)
            if sync_uuid_discovered:
                event_queue.put((key, value, time()))
                logger.prn_inf("found KV pair in stream: {{%s;%s}}"% (key, value))
            else:
                if key == 'sync':
                    if value == sync_uuid:
                        sync_uuid_discovered = True
                        event_queue.put((key, value, time()))
                        logger.prn_inf("found KV pair in stream: {{%s;%s}}, queued..."% (key, value))
                    else:
                        logger.prn_wrn("found SYNC pair in stream: {{%s;%s}}, queued..."% (key, value))
                else:
                    logger.prn_inf("found KV pair in stream: {{%s;%s}}, ignoring..."% (key, value))
