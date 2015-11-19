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

    def server_init(self, port=32765):
        """
        Note:
        On Windows 7 call to socket.getfqdn() gives . (Fully qualified domain name)
        In order for socket.gethostbyname() to work it expects that computer's full name is like ..

        The full computer name may not be in . format. In that case socket.gethostbyname()
        fails to resolve socket.getfqdn() (.) into the IP address.

        Possible solutions:
        By configuration: Follow the link for steps for configuring DNS suffix:
        https://technet.microsoft.com/en-us/library/cc786695(v=ws.10).aspx

        In code: If gethostbyname() fail for FQDN then try host name.
        As hostname resolution to IP succeeds.
        """
        self.SERVER_IP = str(socket.gethostbyname(socket.getfqdn()))
        self.SERVER_PORT = port

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
        self.server_init()
        self.serial_handshake(selftest)

        Sv4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        Sv4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        Sv4.bind(('', self.SERVER_PORT))
        while True:
            (data, address) = Sv4.recvfrom(4096)
            if data and address:
                Sv4.sendto(data, address)
