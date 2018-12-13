"""
mbed SDK
Copyright (c) 2016-2016,2018 ARM Limited

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
from pyocd.core.helpers import ConnectHelper
from pyocd.flash.loader import FileProgrammer


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
        with ConnectHelper.session_with_chosen_probe(unique_id=target_id, resume_on_disconnect=False) as session:
            # Performance hack!
            # Eventually pyOCD will know default clock speed
            # per target
            test_clock = 10000000
            target_type = session.board.target_type
            if target_type == "nrf51":
                # Override clock since 10MHz is too fast
                test_clock = 1000000
            if target_type == "ncs36510":
                # Override clock since 10MHz is too fast
                test_clock = 1000000

            # Configure link
            session.probe.set_clock(test_clock)

            # Program the file
            programmer = FileProgrammer(session)
            programmer.program(image_path)

        return True


def load_plugin():
    """ Returns plugin available in this module
    """
    return HostTestPluginCopyMethod_pyOCD()
