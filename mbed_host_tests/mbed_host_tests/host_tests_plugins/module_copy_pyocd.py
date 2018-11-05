"""
mbed SDK
Copyright (c) 2016-2016 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Russ Butler <russ.butler@arm.com>
"""

import os
from .host_test_plugins import HostTestPluginBase
from pyOCD.board import MbedBoard
from intelhex import IntelHex
import itertools


def _enum_continguous_addr_start_end(addr_list):
    """Generator to get contiguous address ranges with start and end address"""
    for _, b in itertools.groupby(enumerate(addr_list), lambda x_y: x_y[1] - x_y[0]):
        b = list(b)
        yield b[0][1], b[-1][1]


class HostTestPluginCopyMethod_pyOCD(HostTestPluginBase):
    # Plugin interface
    name = 'HostTestPluginCopyMethod_pyOCD'
    type = 'CopyMethod'
    stable = True
    capabilities = ['pyocd']
    required_parameters = ['image_path', 'target_id']

    def __init__(self):
        """ ctor
        """
        HostTestPluginBase.__init__(self)

    def setup(self, *args, **kwargs):
        """ Configure plugin, this function should be called before plugin execute() method is used.
        """
        return True

    def execute(self, capability, *args, **kwargs):
        """! Executes capability by name

        @param capability Capability name
        @param args Additional arguments
        @param kwargs Additional arguments
        @return Capability call return value
        """
        if not self.check_parameters(capability, *args, **kwargs):
            return False

        if not kwargs['image_path']:
            self.print_plugin_error("Error: image path not specified")
            return False

        if not kwargs['target_id']:
            self.print_plugin_error("Error: Target ID")
            return False

        target_id = kwargs['target_id']
        image_path = os.path.normpath(kwargs['image_path'])
        with MbedBoard.chooseBoard(board_id=target_id) as board:
            # Performance hack!
            # Eventually pyOCD will know default clock speed
            # per target
            test_clock = 10000000
            target_type = board.getTargetType()
            if target_type == "nrf51":
                # Override clock since 10MHz is too fast
                test_clock = 1000000
            if target_type == "ncs36510":
                # Override clock since 10MHz is too fast
                test_clock = 1000000

            # Configure link
            board.link.set_clock(test_clock)
            board.link.set_deferred_transfer(True)

            # Collect address, data pairs for programming
            program_list = []
            extension = os.path.splitext(image_path)[1]
            if extension == '.bin':
                # Binary file format
                memory_map = board.target.getMemoryMap()
                rom_region = memory_map.getBootMemory()
                with open(image_path, "rb") as file_handle:
                    program_data = file_handle.read()
                program_list.append((rom_region.start, program_data))
            elif extension == '.hex':
                # Intel hex file format
                ihex = IntelHex(image_path)
                addresses = ihex.addresses()
                addresses.sort()
                for start, end in _enum_continguous_addr_start_end(addresses):
                    size = end - start + 1
                    data = ihex.tobinarray(start=start, size=size)
                    data = bytearray(data)
                    program_list.append((start, data))
            else:
                # Unsupported
                raise Exception("Unsupported file format %s" % extension)

            # Program data
            flash_builder = board.flash.getFlashBuilder()
            for addr, data in program_list:
                flash_builder.addData(addr, list(bytearray(data)))
            flash_builder.program()

            # Read back and verify programming was successful
            for addr, data in program_list:
                read_data = board.target.readBlockMemoryUnaligned8(addr,
                                                                   len(data))
                read_data = bytearray(read_data)
                if bytes(data) != bytes(read_data):
                    raise Exception("Flash programming error - failed to "
                                    "program address 0x%x size %s" %
                                    (addr, len(data)))

            # Cleanup
            board.uninit(resume=False)

        return True


def load_plugin():
    """ Returns plugin available in this module
    """
    return HostTestPluginCopyMethod_pyOCD()
