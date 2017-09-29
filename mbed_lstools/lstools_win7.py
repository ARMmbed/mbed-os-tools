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
import os
import sys
import string

from .lstools_base import MbedLsToolsBase

import logging

logger = logging.getLogger("mbedls.lstools_win7")


class MbedLsToolsWin7(MbedLsToolsBase):
    """ mbed-enabled platform detection for Windows
    """
    def __init__(self, **kwargs):
        MbedLsToolsBase.__init__(self, **kwargs)
        self.os_supported.append('Windows7')
        if sys.version_info[0] < 3:
            import _winreg as winreg
        else:
            import winreg

    def find_candidates(self):
        return [
            {
                'mount_point': mnt,
                'target_id_usb_id': id,
                'serial_port': self._com_port(id)
            }
            for mnt, id in self.get_mbeds()
            if self.mount_point_ready(mnt)
        ]

    def _com_port(self, tid):
        """! Function checks mbed serial port in Windows registry entries
        @param tid TargetID
        @return Returns None if port is not found. In normal circumstances it should never return None
        @details This goes through a whole new loop, but this assures that even if serial port (COM)
                 is not detected, we still get the rest of info like mount point etc.
        """
        winreg.Enum = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Enum')
        usb_devs = winreg.OpenKey(winreg.Enum, 'USB')

        logger.debug('get_mbed_com_port ID: %s', tid)

        # first try to find all devs keys (by tid)
        dev_keys = []
        for vid in self.iter_keys(usb_devs):
            try:
                dev_keys += [winreg.OpenKey(vid, tid)]
            except:
                pass

        # then try to get port directly from "Device Parameters"
        for key in dev_keys:
            try:
                param = winreg.OpenKey(key, "Device Parameters")
                port = winreg.QueryValueEx(param, 'PortName')[0]
                logger.debug('get_mbed_com_port port %s', port)
                return port
            except:
                pass

        # else follow symbolic dev links in registry
        for key in dev_keys:
            try:
                ports = []
                parent_id = winreg.QueryValueEx(key, 'ParentIdPrefix')[0]
                for VID in self.iter_keys(usb_devs):
                    for dev in self.iter_keys_as_str(VID):
                        if parent_id in dev:
                            ports += [self.get_mbed_com_port(dev)]
                for port in ports:
                    if port:
                        logger.debug("get_mbed_com_port port %s", port)
                        return port
            except:
                pass

        # Check for a target USB ID from tid
        target_usb_ids = self.get_connected_mbeds_usb_ids()
        if tid in target_usb_ids:
            if target_usb_ids[tid] != tid:
                # Try again with the target USB ID
                return self.get_mbed_com_port(target_usb_ids[tid])

        # If everything fails, return None
        return None

    def get_connected_mbeds_usb_ids(self):
        """! Function  return mbeds with existing mount point's
             target ID mapped to their target USB ID
        @return Returns {<target_id>: <target_usb_id>, ...}
        @details Helper function
        """
        connected_mbeds_ids = {}
        for mbed in self.get_connected_mbeds():
            target_id, htm_target_id = self.get_mbed_target_id(mbed[0], mbed[1])
            connected_mbeds_ids[target_id] = mbed[1]
        return connected_mbeds_ids

    def get_mbeds(self):
        """! Function filters devices' mount points for valid TargetID
        @return Returns [(<mbed_mount_point>, <mbed_id>), ..]
        @details TargetID should be a hex string with 10-48 chars
        """
        mbeds = []
        for mbed in self.get_mbed_devices():
            mountpoint = re.match('.*\\\\(.:)$', mbed[0]).group(1)
            # TargetID is a hex string with 10-48 chars
            m = re.search('[&#]([0-9A-Za-z]{10,48})[&#]', mbed[1])
            if not m:
                continue
            tid = m.group(1)
            mbeds += [(mountpoint, tid)]
            logger.debug((mountpoint, tid))
        return mbeds

    # =============================== Registry ====================================

    def iter_keys_as_str(self, key):
        """! Iterate over subkeys of a key returning subkey as string
        """
        for i in range(winreg.QueryInfoKey(key)[0]):
            yield winreg.EnumKey(key, i)

    def iter_keys(self, key):
        """! Iterate over subkeys of a key
        """
        for i in range(winreg.QueryInfoKey(key)[0]):
            yield winreg.OpenKey(key, winreg.EnumKey(key, i))

    def iter_vals(self, key):
        """! Iterate over values of a key
        """
        for i in range(winreg.QueryInfoKey(key)[1]):
            yield winreg.EnumValue(key, i)

    def get_mbed_devices(self):
        """! Get MBED devices (connected or not)
        @return List of devices
        @details Note: We will detect also non-standard MBED devices mentioned on 'usb_vendor_list' list.
                 This will help to detect boards like EFM boards.
        """
        result = []
        for ven in self.usb_vendor_list:
            result += [d for d in self.get_dos_devices() if ven.upper() in d[1].upper()]

        logger.debug("get_mbed_devices result %s", result)
        return result

    def get_dos_devices(self):
        """! Get DOS devices (connected or not)
        """
        ddevs = [dev for dev in self.get_mounted_devices() if 'DosDevices' in dev[0]]
        return [(d[0], self.regbin2str(d[1])) for d in ddevs]

    def get_mounted_devices(self):
        """! Get all mounted devices (connected or not)
        """
        mounts = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\MountedDevices')
        return [val for val in self.iter_vals(mounts)]

    def regbin2str(self, regbin):
        """! Decode registry binary to readable string
        """
        return ''.join(filter(lambda ch: ch in string.printable, regbin.decode('ascii', errors='ignore')))
