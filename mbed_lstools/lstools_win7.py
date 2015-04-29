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

import re
import os
import sys

from lstools_base import MbedLsToolsBase


class MbedLsToolsWin7(MbedLsToolsBase):
    def __init__(self):
        """ MbedLsToolsWin7 supports mbed enabled platforms detection across Windows7 OS family
        """
        MbedLsToolsBase.__init__(self)
        self.os_supported.append('Windows7')
        if sys.version_info[0] < 3:
            import _winreg as winreg
        else:
            import winreg
        self.winreg = winreg

    def list_mbeds(self):
        """Returns connected mbeds as an mbeds dictionary
        """
        mbeds = []
        for mbed in self.discover_connected_mbeds(self.manufacture_ids):
            d = {}
            d['mount_point']   = mbed[0] if mbed[0] else None
            d['target_id']     = mbed[1] if mbed[1] else None
            d['serial_port']   = mbed[2] if mbed[2] else None
            d['platform_name'] = mbed[3] if mbed[3] else None
            mbeds += [d]
        return mbeds

    def discover_connected_mbeds(self, defs={}):
        """ Returns [(<mbed_mount_point>, <mbed_id>, <com port>, <board model>), ..]
            Notice: this function is permissive: adds new elements in-places when and if found
        """
        mbeds = [(m[0], m[1], None, None) for m in self.get_connected_mbeds()]
        for i in range(len(mbeds)):
            mbed = mbeds[i]
            mnt, mbed_id = mbed[0], mbed[1]
            mbed_id_prefix = mbed_id[0:4]
            # Deducing mbed-enabled TargetID based on available targetID definition DB.
            # If TargetID from USBID is not recognized we will try to check URL in mbed.htm
            if mbed_id_prefix not in defs:
                mbed_htm_target_id = self.get_mbed_htm_target_id(mnt)
                mbed_id = mbed_htm_target_id if mbed_htm_target_id is not None else mbed_id
            mbed_id_prefix = mbed_id[0:4]
            board = defs[mbed_id_prefix] if mbed_id_prefix in defs else None
            mbeds[i] = (mnt, mbed_id, mbeds[i][2], board)

            port = self.get_mbed_com_port(mbed[1])
            if port:
                mbeds[i] = (mnt, mbed_id, port, mbeds[i][3])
        return mbeds

    def get_mbed_com_port(self, id):
        """ This goes through a whole new loop, but this assures that even if
            serial port (COM) is not detected, we still get the rest of info like mount point etc.
        """
        self.winreg.Enum = self.winreg.OpenKey(self.winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Enum')
        usb_devs = self.winreg.OpenKey(self.winreg.Enum, 'USB')

        if self.DEGUB_FLAG:
            self.debug(self.get_mbed_com_port.__name__, 'ID: ' + id)

        # first try to find all devs keys (by id)
        dev_keys = []
        for vid in self.iter_keys(usb_devs):

            if self.DEGUB_FLAG:
                self.debug(self.get_mbed_com_port.__name__, (vid, id))

            try:
                dev_keys += [self.winreg.OpenKey(vid, id)]
            except:
                pass

        # then try to get port directly from "Device Parameters"
        for key in dev_keys:
            try:
                param = self.winreg.OpenKey(key, "Device Parameters")
                port = self.winreg.QueryValueEx(param, 'PortName')[0]
                if self.DEGUB_FLAG:
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
                        if self.DEGUB_FLAG:
                            self.debug(self.get_mbed_com_port.__name__, port)
                        return port
            except:
                pass

    def get_connected_mbeds(self):
        """ Returns [(<mbed_mount_point>, <mbed_id>), ..]
        """
        return [m for m in self.get_mbeds() if os.path.exists(m[0])]

    def get_mbeds(self):
        """ Returns [(<mbed_mount_point>, <mbed_id>), ..]
        """
        mbeds = []
        for mbed in self.get_mbed_devices():
            mountpoint = re.match('.*\\\\(.:)$', mbed[0]).group(1)
            # id is a hex string with 10-36 chars
            id = re.search('[0-9A-Fa-f]{10,48}', mbed[1]).group(0)
            mbeds += [(mountpoint, id)]
            if self.DEGUB_FLAG:
                self.debug(self.get_mbeds.__name__, (mountpoint, id))
        return mbeds

    # =============================== Registry ====================================

    def iter_keys_as_str(self, key):
        """ Iterate over subkeys of a key returning subkey as string
        """
        for i in range(self.winreg.QueryInfoKey(key)[0]):
            yield self.winreg.EnumKey(key, i)

    def iter_keys(self, key):
        """ Iterate over subkeys of a key
        """
        for i in range(self.winreg.QueryInfoKey(key)[0]):
            yield self.winreg.OpenKey(key, self.winreg.EnumKey(key, i))

    def iter_vals(self, key):
        """ Iterate over values of a key
        """
        for i in range(self.winreg.QueryInfoKey(key)[1]):
            yield self.winreg.EnumValue(key, i)

    def get_mbed_devices(self):
        """ Get MBED devices (connected or not)
            Note: We will detect also non-standard MBED devices mentioned on 'usb_vendor_list' list.
                  This will help to detect boards like EFM boards.
        """
        result = []
        for ven in self.usb_vendor_list:
            result += [d for d in self.get_dos_devices() if ven.upper() in d[1].upper()]
        if self.DEGUB_FLAG:
            self.debug(self.get_mbed_devices.__name__, result)
        return result

    def get_dos_devices(self):
        """ Get DOS devices (connected or not)
        """
        ddevs = [dev for dev in self.get_mounted_devices() if 'DosDevices' in dev[0]]
        return [(d[0], self.regbin2str(d[1])) for d in ddevs]

    def get_mounted_devices(self):
        """ Get all mounted devices (connected or not)
        """
        devs = []
        mounts = self.winreg.OpenKey(self.winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\MountedDevices')
        for i in range(self.winreg.QueryInfoKey(mounts)[1]):
            devs += [self.winreg.EnumValue(mounts, i)]
        return devs

    def regbin2str(self, binary):
        """ Decode registry binary to readable string
        """
        string = ''
        for i in range(0, len(binary), 2):
            # binary[i] is str in Python2 and int in Python3
            if isinstance(binary[i], int):
                if binary[i] < 128:
                    string += chr(binary[i])
            elif isinstance(binary[i], str):
                string += binary[i]
            else:
                string = None
                break
        if self.DEGUB_FLAG:
            self.debug(self.regbin2str.__name__, string)
        return string
