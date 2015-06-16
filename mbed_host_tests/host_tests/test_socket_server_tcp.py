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

class TCPSocketServerEchoExtTest(BaseHostTest):
    """ This echo server opens and closes connections.
    """

    def send_server_ip_port(self, selftest, ip_address, port_no):
        """ Set up network host. Reset target and and send server IP via serial to Mbed
        """
        c = selftest.mbed.serial_readline() # 'TCPCllient waiting for server IP and port...'
        if c is None:
            self.print_result(selftest.RESULT_IO_SERIAL)
            return

        selftest.notify(c.strip())
        selftest.notify("HOST: Sending server IP Address to target...")

        connection_str = ip_address + ":" + str(port_no) + "\n"
        selftest.mbed.serial_write(connection_str)
        selftest.notify(connection_str)

        # Serial port handshake is finished
        selftest.dump_serial()  # We want to dump serial port while test is ongoing

    def test(self, selftest):
        SERVER_IP = str(socket.gethostbyname(socket.getfqdn()))
        SERVER_PORT = 32767

        selftest.notify("HOST: Listening for TCP connections: " + SERVER_IP + ":" + str(SERVER_PORT))
        self.send_server_ip_port(selftest, SERVER_IP, SERVER_PORT)

        selftest.notify("HOST: Init sockets...")
        Sv4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Sv4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        Sv4.bind(('', SERVER_PORT))

        Sv4.listen(1)
        selftest.notify("HOST: Listening for TCP connections: " + SERVER_IP + ":" + str(SERVER_PORT))
        try:
            for i in range(0, 2):
                (clientsocket, address) = Sv4.accept()
                selftest.notify('HOST: Connection received from ' + str(address))
                while True:
                    try:
                        data = clientsocket.recv(4096)
                    except:
                        data = None
                        break
                    clientsocket.sendall(data)
                selftest.notify('HOST: connection closed')
                clientsocket.close()
        finally:
            Sv4.close()
