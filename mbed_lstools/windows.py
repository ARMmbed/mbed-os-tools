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
DEBUG = logging.DEBUG
del logging

if sys.version_info[0] < 3:
    import _winreg as winreg
else:
    import winreg


class MbedLsToolsWin7(MbedLsToolsBase):
    """ mbed-enabled platform detection for Windows
    """
    def __init__(self, **kwargs):
        MbedLsToolsBase.__init__(self, **kwargs)
        self.os_supported.append('Windows7')

    def find_candidates(self):
        return [
            {
                'mount_point': mnt,
                'target_id_usb_id': id,
                'serial_port': self._com_port(id)
            }
            for mnt, id in self.get_mbeds()
        ]

    def _com_port(self, tid):
        """! Function checks mbed serial port in Windows registry entries
        @param tid TargetID
        @return Returns None if port is not found. In normal circumstances it should never return None
        @details This goes through a whole new loop, but this assures that even if serial port (COM)
                 is not detected, we still get the rest of info like mount point etc.
        """
        winreg.Enum = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                     r'SYSTEM\CurrentControlSet\Enum')
        usb_devs = winreg.OpenKey(winreg.Enum, 'USB')
        logger.debug("_com_port usb_devs %r",
                     list(self.iter_keys_as_str(usb_devs)))

        logger.debug("_com_port looking up usb id in all usb devices")
        dev_keys = []
        for name, vid in zip(self.iter_keys_as_str(usb_devs),
                             self.iter_keys(usb_devs)):
            try:
                dev_keys.append(winreg.OpenKey(vid, tid))
                if logger.isEnabledFor(DEBUG):
                    logger.debug(
                        "Found usb id %s in %s with subkeys %r", tid, name,
                        list(self.iter_keys_as_str(winreg.OpenKey(vid, tid))))
            except OSError:
                pass

        logger.debug("_com_port Detecting port with Device Parameter")
        for key in dev_keys:
            try:
                param = winreg.OpenKey(key, "Device Parameters")
                port, regtype = winreg.QueryValueEx(param, 'PortName')
                logger.debug('_com_port port %r regtype %r', port, regtype)
                return port
            except OSError as e:
                logger.debug("Exception %r %s", key, str(e))
                pass

        logger.debug("_com_port Detecting port by following symlinks")
        for key in dev_keys:
            try:
                ports = []
                parent_id, regtype = winreg.QueryValueEx(key, 'ParentIdPrefix')
                logger.debug("_com_port parent_id %r regtype %r")
                for VID in self.iter_keys(usb_devs):
                    candidate_keys = [k for k in self.iter_keys_as_str(VID)
                                      if parent_id in k]
                    for dev in candidate_keys:
                        logger.debug(
                            "_com_port recursive port detection with %r", dev)
                        maybe_port = self._com_port(dev)
                        if maybe_port:
                            return maybe_port
            except OSError as e:
                logger.debug("Exception %r %s", key, str(e))
                pass

        # If everything fails, return None
        return None


    def _mount_point_exists(self, mountpoint):
        """! Function returns if the mountpoint exists
        @param mountpoint Path of mountpoint
        @return Returns True if mountpoint exists, otherwise False
        @details This uses a Windows subcommand to avoid throwing a Python
        error box when the device is in an ejected state.
        """
        cmd = ['dir', mountpoint]
        logger.debug('running command: %s' % (' '.join(cmd)))
        stdout, stderr, retval = self._run_cli_process(cmd)

        if not retval:
            logger.debug("mountpoint %s ready" % mountpoint)
        else:
            logger.debug("mountpoint %s reported not ready with error '%s'" %
                (mountpoint, stderr.strip()))

        return not retval


    def get_mbeds(self):
        """! Function filters devices' mount points for valid TargetID
        @return Returns [(<mbed_mount_point>, <mbed_id>), ..]
        @details TargetID should be a hex string with 10-48 chars
        """
        mbeds = []
        for mbed in self.get_mbed_devices():
            mountpoint = re.match('.*\\\\(.:)$', mbed[0]).group(1)
            logger.debug('Registry mountpoint %s', mountpoint)

            if self._mount_point_exists(mountpoint):
                # TargetID is a hex string with 10-48 chars
                m = re.search('[&#]([0-9A-Za-z]{10,48})[&#]', mbed[1])
                if not m:
                    continue
                tid = m.group(1)
                mbeds += [(mountpoint, tid)]
                logger.debug("get_mbeds mount_point %s usb_id %s", mountpoint, tid)
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
        logger.debug("iter_vals %r", key)
        for i in range(winreg.QueryInfoKey(key)[1]):
            yield winreg.EnumValue(key, i)

    def get_mbed_devices(self):
        """! Get MBED devices (connected or not)
        @return List of devices
        @details Note: We will detect also non-standard MBED devices mentioned on 'usb_vendor_list' list.
                 This will help to detect boards like EFM boards.
        """
        upper_ven = [ven.upper() for ven in self.usb_vendor_list]
        mounts_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\MountedDevices')
        for point, label, _ in self.iter_vals(mounts_key):
            printable_label = label.decode('utf-16le', 'ignore')
            if ('DosDevices' in point and
                any(v in printable_label.upper() for v in upper_ven)):
                logger.debug("Found Mount point %s with usb ID %s",point,
                             printable_label)
                yield (point, printable_label)
            else:
                logger.debug("Skipping Mount point %r label %r", point, label)
