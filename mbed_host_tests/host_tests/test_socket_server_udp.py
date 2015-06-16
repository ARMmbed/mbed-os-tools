"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

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

import socket
from . import BaseHostTest

class UDPSocketServerEchoExtTest(BaseHostTest):

    def __init__(self):
        self.SERVER_IP = str(socket.gethostbyname(socket.getfqdn()))
        self.SERVER_PORT = 32765

    def serial_handshake(self, selftest):
        print "HOST: Listening for UDP connections..."

        c = selftest.mbed.serial_readline() # 'UDPCllient waiting for server IP and port...'
        if c is None:
            selftest.print_result(selftest.RESULT_IO_SERIAL)
            return
        selftest.notify(c.strip())

        selftest.notify("HOST: Sending server IP Address to target...")
        connection_str = self.SERVER_IP + ":" + str(self.SERVER_PORT) + "\n"
        selftest.mbed.serial_write(connection_str)

        # Serial port handshake is finished
        selftest.dump_serial()  # We want to dump serial port while test is ongoing

    def test(self, selftest):
        self.serial_handshake(selftest)

        Sv4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        Sv4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        Sv4.bind(('', self.SERVER_PORT))
        while True:
            (data, address) = Sv4.recvfrom(4096)
            if data and address:
                Sv4.sendto(data, address)
