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


class MbedLsToolsWin7(MbedLsToolsBase):
    """ Class derived from MbedLsToolsBase ports mbed-ls functionality for Windows 7 OS
    """
    def __init__(self, **kwargs):
        """ MbedLsToolsWin7 supports mbed enabled platforms detection across Windows7 OS family
        """
        MbedLsToolsBase.__init__(self, **kwargs)
        self.os_supported.append('Windows7')
        if sys.version_info[0] < 3:
            import _winreg as winreg
        else:
            import winreg
        self.winreg = winreg

    def list_mbeds(self):
        """! Returns detailed list of connected mbeds
            @return Returns list of structures with detailed info about each mbed
            @details Function returns list of dictionaries with mbed attributes such as mount point, TargetID name etc.
        """
        self.ERRORLEVEL_FLAG = 0

        mbeds = []
        for mbed in self.discover_connected_mbeds(self.manufacture_ids):
            d = {}
            d['mount_point'] = mbed[0] if mbed[0] else None
            d['target_id'] = mbed[1] if mbed[1] else None
            d['serial_port'] = mbed[2] if mbed[2] else None
            d['platform_name'] = mbed[3] if mbed[3] else None
            d['target_id_usb_id'] = mbed[4] if mbed[4] else None
            d['target_id_mbed_htm'] = mbed[5] if mbed[5] else None
            mbeds += [d]

            if None in mbed:
                self.ERRORLEVEL_FLAG = -1

        return mbeds

    def discover_connected_mbeds(self, defs={}):
        """! Function produces list of mbeds with additional information and bind mbed with correct TargetID
            @return Returns [(<mbed_mount_point>, <mbed_id>, <com port>, <board model>,
                              <usb_target_id>, <htm_target_id>), ..]
            @details Notice: this function is permissive: adds new elements in-places when and if found
        """
        mbeds = [(m[0], m[1], None, None) for m in self.get_connected_mbeds()]
        for i in range(len(mbeds)):
            mbed = mbeds[i]
            mnt = mbed[0]
            mbed_id, mbed_htm_target_id = self.get_mbed_target_id(mnt, mbed[1])
            mbed_id_prefix = mbed_id[0:4]
            board = defs[mbed_id_prefix] if mbed_id_prefix in defs else None
            port = self.get_mbed_com_port(mbed[1])
            mbeds[i] = (mnt, mbed_id, port, board, mbed[1], mbed_htm_target_id)
        return mbeds

    def get_mbed_com_port(self, tid):
        """! Function checks mbed serial port in Windows registry entries
        @param tid TargetID
        @return Returns None if port is not found. In normal circumstances it should never return None
        @details This goes through a whole new loop, but this assures that even if serial port (COM)
                 is not detected, we still get the rest of info like mount point etc.
        """
        self.winreg.Enum = self.winreg.OpenKey(self.winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Enum')
        usb_devs = self.winreg.OpenKey(self.winreg.Enum, 'USB')

        self.debug(self.get_mbed_com_port.__name__, 'ID: ' + tid)

        # first try to find all devs keys (by tid)
        dev_keys = []
        for vid in self.iter_keys(usb_devs):
            try:
                dev_keys += [self.winreg.OpenKey(vid, tid)]
            except:
                pass

        # then try to get port directly from "Device Parameters"
        for key in dev_keys:
            try:
                param = self.winreg.OpenKey(key, "Device Parameters")
                port = self.winreg.QueryValueEx(param, 'PortName')[0]
                self.debug(self.get_mbed_com_port.__name__, port)
                return port
            except:
                pass

        # else follow symbolic dev links in registry
        for key in dev_keys:
            try:
                ports = []
                parent_id = self.winreg.QueryValueEx(key, 'ParentIdPrefix')[0]
                for VID in self.iter_keys(usb_devs):
                    for dev in self.iter_keys_as_str(VID):
                        if parent_id in dev:
                            ports += [self.get_mbed_com_port(dev)]
                for port in ports:
                    if port:
                        self.debug(self.get_mbed_com_port.__name__, port)
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

    def get_connected_mbeds(self):
        """! Function  return mbeds with existing mount point
        @return Returns [(<mbed_mount_point>, <mbed_id>), ..]
        @details Helper function
        """
        return [m for m in self.get_mbeds() if self.mount_point_ready(m[0])]

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
            self.debug(self.get_mbeds.__name__, (mountpoint, tid))
        return mbeds

    def get_mbed_target_id(self, mnt, target_usb_id):
        """! Function gets the mbed target and HTM IDs
        @param mnt mbed mount point (disk / drive letter)
        @param target_usb_id mbed target USB ID
        @return Function returns (<target_id>, <htm_target_id>)
        @details Helper function
        """
        mbed_htm_target_id = self.get_mbed_htm_target_id(mnt)
        # Deducing mbed-enabled TargetID based on available targetID definition DB.
        # If TargetID from USBID is not recognized we will try to check URL in mbed.htm
        mbed_id = mbed_htm_target_id if mbed_htm_target_id is not None else target_usb_id
        return mbed_id, mbed_htm_target_id

    # =============================== Registry ====================================

    def iter_keys_as_str(self, key):
        """! Iterate over subkeys of a key returning subkey as string
        """
        for i in range(self.winreg.QueryInfoKey(key)[0]):
            yield self.winreg.EnumKey(key, i)

    def iter_keys(self, key):
        """! Iterate over subkeys of a key
        """
        for i in range(self.winreg.QueryInfoKey(key)[0]):
            yield self.winreg.OpenKey(key, self.winreg.EnumKey(key, i))

    def iter_vals(self, key):
        """! Iterate over values of a key
        """
        for i in range(self.winreg.QueryInfoKey(key)[1]):
            yield self.winreg.EnumValue(key, i)

    def get_mbed_devices(self):
        """! Get MBED devices (connected or not)
        @return List of devices
        @details Note: We will detect also non-standard MBED devices mentioned on 'usb_vendor_list' list.
                 This will help to detect boards like EFM boards.
        """
        result = []
        for ven in self.usb_vendor_list:
            result += [d for d in self.get_dos_devices() if ven.upper() in d[1].upper()]

        for r in result:
            self.debug(self.get_mbed_devices.__name__, r)
        return result

    def get_dos_devices(self):
        """! Get DOS devices (connected or not)
        """
        ddevs = [dev for dev in self.get_mounted_devices() if 'DosDevices' in dev[0]]
        return [(d[0], self.regbin2str(d[1])) for d in ddevs]

    def get_mounted_devices(self):
        """! Get all mounted devices (connected or not)
        """
        mounts = self.winreg.OpenKey(self.winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\MountedDevices')
        return [val for val in self.iter_vals(mounts)]

    def regbin2str(self, regbin):
        """! Decode registry binary to readable string
        """
        return filter(lambda ch: ch in string.printable, regbin)

    def mount_point_ready(self, path):
        """! Check if a mount point is ready for file operations
        @return Returns True if the given path exists, False otherwise
        @details Calling the Windows command `dir` instead of using the python
        `os.path.exists`. The latter causes a Python error box to appear claiming
        there is "No Disk" for some devices that are in the ejected state. Calling
        `dir` prevents this since it uses the Windows API to determine if the
        device is ready before accessing the file system.
        """
        stdout, stderr, retcode = self.run_cli_process('dir %s' % path)
        result = True if retcode == 0 else False

        if result:
            self.debug(self.mount_point_ready.__name__, "Mount point %s is ready" % path)
        else:
            self.debug(self.mount_point_ready.__name__, "Mount point %s reported not ready with error '%s'" % (path, stderr.strip()))

        return result
