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
from os.path import join, isdir, dirname, abspath
import os

from .lstools_base import MbedLsToolsBase

import logging
logger = logging.getLogger("mbedls.lstools_linux")
del logging

def _readlink(link):
    content = os.readlink(link)
    if content.startswith(".."):
        return abspath(join(dirname(link), content))
    else:
        return content


class MbedLsToolsLinuxGeneric(MbedLsToolsBase):
    """ mbed-enabled platform for Linux with udev
    """
    def __init__(self, **kwargs):
        """! ctor
        """
        MbedLsToolsBase.__init__(self, **kwargs)
        self.nlp = re.compile(
            r'(pci|usb)-[0-9a-zA-Z_-]*_(?P<usbid>[0-9a-zA-Z]*)-.*$')
        self.mmp = re.compile(
            r'(?P<dev>(/[^/ ]*)+) on (?P<dir>(/[^/ ]*)+) ')

    def find_candidates(self):
        disk_ids = self._dev_by_id('disk')
        serial_ids = self._dev_by_id('serial')
        mount_ids = dict(self._fat_mounts())
        logger.debug("Mount mapping %r", mount_ids)

        return [
            {
                'mount_point' : mount_ids.get(disk_dev),
                'serial_port' : serial_ids.get(disk_uuid),
                'target_id_usb_id' : disk_uuid
            } for disk_uuid, disk_dev in disk_ids.items()
        ]

    def _dev_by_id(self, device_type):
        """! Get a dict, USBID -> device, for a device class
        @param device_type The type of devices to search. For exmaple, "serial"
          looks for all serial devices connected to this computer
        @return A dict: Device USBID -> device file in /dev
        """
        dir = join("/dev", device_type, "by-id")
        if isdir(dir):
            to_ret = dict(self._hex_ids([join(dir, f) for f in os.listdir(dir)]))
            logger.debug("Found %s devices by id %r", device_type, to_ret)
            return to_ret
        else:
            logger.error("Could not get %s devices by id. "
                         "This could be because your Linux distribution "
                         "does not use udev, or does not create /dev/%s/by-id "
                         "symlinks. Please submit an issue to github.com/"
                         "armmbed/mbed-ls.", device_type, device_type)
            return {}

    def _fat_mounts(self):
        """! Lists mounted devices with vfat file system (potential mbeds)
        @result Returns list of all mounted vfat devices
        @details Uses Linux shell command: 'mount'
        """
        _stdout, _, retval = self._run_cli_process('mount')
        if not retval:
            for line in _stdout.splitlines():
                if b'vfat' in line:
                    match = self.mmp.search(line.decode('utf-8'))
                    if match:
                        yield match.group("dev"), match.group("dir")

    def _hex_ids(self, dev_list):
        """! Build a USBID map for a device list
        @param disk_list List of disks in a system with USBID decoration
        @return Returns map USBID -> device file in /dev
        @details Uses regular expressions to get a USBID (TargeTIDs) a "by-id"
          symbolic link
        """
        logger.debug("Converting device list %r", dev_list)
        for dl in dev_list:
            match = self.nlp.search(dl)
            if match:
                yield match.group("usbid"), _readlink(dl)
