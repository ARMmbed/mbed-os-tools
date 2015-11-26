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

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""

import os
import sys
import platform

from os import access, F_OK
from sys import stdout
from time import sleep
from subprocess import call


class HostTestPluginBase:
    """ Base class for all plugins used with host tests
    """
    ###########################################################################
    # Interface:
    ###########################################################################

    ###########################################################################
    # Interface attributes defining plugin name, type etc.
    ###########################################################################
    name = "HostTestPluginBase" # Plugin name, can be plugin class name
    type = "BasePlugin"         # Plugin type: ResetMethod, Copymethod etc.
    capabilities = []           # Capabilities names: what plugin can achieve
                                # (e.g. reset using some external command line tool)
    required_parameters = []    # Parameters required for 'kwargs' in plugin APIs: e.g. self.execute()
    stable = False              # Determine if plugin is stable and can be used

    ###########################################################################
    # Interface methods
    ###########################################################################
    def setup(self, *args, **kwargs):
        """ Configure plugin, this function should be called before plugin execute() method is used.
        """
        return False

    def execute(self, capability, *args, **kwargs):
        """! Executes capability by name

        @param capability Capability name
        @param args Additional arguments
        @param kwargs Additional arguments

        @details Each capability e.g. may directly just call some command line program or execute building pythonic function

        @return Capability call return value
        """
        return False

    def is_os_supported(self, os_name=None):
        """!
        @return Returns true if plugin works (supportes) under certain OS
        @os_name String describing OS.
                 See self.mbed_os_support() and self.mbed_os_info()
        @details In some cases a plugin will not work under particular OS
                 mainly because command / software used to implement plugin
                 functionality is not available e.g. on MacOS or Linux.
        """
        return True

    ###########################################################################
    # Interface helper methods - overload only if you need to have custom behaviour
    ###########################################################################
    def print_plugin_error(self, text):
        """! Function prints error in console and exits always with False

        @param text Text to print
        """
        print "Plugin error: %s::%s: %s"% (self.name, self.type, text)
        return False

    def print_plugin_info(self, text, NL=True):
        """! Function prints notification in console and exits always with True

        @param text Text to print

        @param NL Newline will be added behind text if this flag is True
        """
        if NL:
            print "Plugin info: %s::%s: %s"% (self.name, self.type, text)
        else:
            print "Plugin info: %s::%s: %s"% (self.name, self.type, text),
        return True

    def print_plugin_char(self, char):
        """ Function prints char on stdout
        """
        stdout.write(char)
        stdout.flush()
        return True

    def check_mount_point_ready(self, destination_disk, init_delay=0.2, loop_delay=0.25):
        """! Waits until destination_disk is ready and can be accessed by e.g. copy commands

        @return True if mount point was ready in given time, False otherwise

        @param destination_disk Mount point (disk) which will be checked for readiness
        @param init_delay - Initial delay time before first access check
        @param loop_delay - polling delay for access check
        """
        result = False
        # Let's wait for 30 * loop_delay + init_delay max
        if not access(destination_disk, F_OK):
            self.print_plugin_info("Waiting for mount point '%s' to be ready..."% destination_disk, NL=False)
            sleep(init_delay)
            for i in range(30):
                if access(destination_disk, F_OK):
                    result = True
                    break
                sleep(loop_delay)
                self.print_plugin_char('.')
        return result

    def check_parameters(self, capability, *args, **kwargs):
        """! This function should be ran each time we call execute() to check if none of the required parameters is missing

        @return Returns True if all parameters are passed to plugin, else return False

        @param capability Capability name
        @param args Additional parameters
        @param kwargs Additional parameters
        """
        missing_parameters = []
        for parameter in self.required_parameters:
            if parameter not in kwargs:
                missing_parameters.append(parameter)
        if len(missing_parameters):
            self.print_plugin_error("execute parameter(s) '%s' missing!"% (', '.join(missing_parameters)))
            return False
        return True

    def run_command(self, cmd, shell=True):
        """! Runs command from command line.

        @param cmd Command to execute
        @param shell True if shell command should be executed (eg. ls, ps)

        @details Function prints 'cmd' return code if execution failed

        @return True if command successfully executed
        """
        result = True
        try:
            ret = call(cmd, shell=shell)
            if ret:
                self.print_plugin_error("[ret=%d] Command: %s"% (int(ret), cmd))
                return False
        except Exception as e:
            result = False
            self.print_plugin_error("[ret=%d] Command: %s"% (int(ret), cmd))
            self.print_plugin_error(str(e))
        return result

    def mbed_os_info(self):
        """! Returns information about host OS

        @return Returns tuple with information about OS and host platform
        """
        result = (os.name,
                  platform.system(),
                  platform.release(),
                  platform.version(),
                  sys.platform)
        return result

    def mbed_os_support(self):
        """! Function used to determine host OS
        @return Returns None if host OS is unknown, else string with name
        @details This function should be ported for new OS support
        """
        result = None
        os_info = self.mbed_os_info()
        if (os_info[0] == 'nt' and os_info[1] == 'Windows'):
            result = 'Windows7'
        elif (os_info[0] == 'posix' and os_info[1] == 'Linux' and ('Ubuntu' in os_info[3])):
            result = 'Ubuntu'
        elif (os_info[0] == 'posix' and os_info[1] == 'Linux'):
            result = 'LinuxGeneric'
        elif (os_info[0] == 'posix' and os_info[1] == 'Darwin'):
            result = 'Darwin'
        return result
