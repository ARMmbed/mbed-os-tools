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

from lstools_base import MbedLsToolsBase


class MbedLsToolsLinuxGeneric(MbedLsToolsBase):
    """ MbedLsToolsLinuxGeneric supports mbed-enabled platforms detection across Linux family
    """
    def __init__(self):
        """! ctor
        """
        MbedLsToolsBase.__init__(self)
        self.os_supported.append('LinuxGeneric')
        self.hex_uuid_pattern = "usb-[0-9a-zA-Z_-]*_([0-9a-zA-Z]*)-.*"
        # Since Ubuntu 15 DAplink serial port device can have pci- prefix, not only usb- one
        self.name_link_pattern = '((%s)-[0-9a-zA-Z_-]*_[0-9a-zA-Z]*-.*$)'% ('|'.join(["pci", "usb"]))
        self.mount_media_pattern = "^/[a-zA-Z0-9/]* on (/[a-zA-Z0-9/]*) "

        self.nlp = re.compile(self.name_link_pattern)
        self.hup = re.compile(self.hex_uuid_pattern)

    def list_mbeds(self):
        """! Returns detailed list of connected mbeds
        @return Returns list of structures with detailed info about each mbed
        @details Function returns list of dictionaries with mbed attributes such as mount point, TargetID name etc.
        Function returns mbed list with platform names if possible
        all_devices =
        [
            ['*not detected', 'sdi', '/media/usb3', '/dev/ttyACM7', 'usb-MBED_microcontroller_066EFF534951775087215736-0:0 -> ../../sdi'],
            ['*not detected', 'sdg', '/media/usb5', '/dev/ttyACM5', 'usb-MBED_microcontroller_066EFF525257775087141721-0:0 -> ../../sdg'],
            ['*not detected', 'sdf', '/media/przemek/NUCLEO', '/dev/ttyACM4', 'usb-MBED_microcontroller_0671FF534951775087131543-0:0 -> ../../sdf'],
            ['*not detected', 'sdd', '/media/usb4', '/dev/ttyACM2', 'usb-MBED_microcontroller_0670FF494951785087152739-0:0 -> ../../sdd'],
            ['*not detected', 'sdb', '/media/usb0', '/dev/ttyACM0', 'usb-MBED_microcontroller_0674FF484951775087083114-0:0 -> ../../sdb'],
            ['*not detected', 'sdh', '/media/usb6', '/dev/ttyACM6', 'usb-MBED_microcontroller_066FFF525257775087155144-0:0 -> ../../sdh'],
            ['*not detected', 'sdc', '/media/usb1', '/dev/ttyACM1', 'usb-MBED_microcontroller_066AFF494956805087155327-0:0 -> ../../sdc'],
            ['*not detected', 'sde', '/media/usb2', '/dev/ttyACM3', 'usb-MBED_microcontroller_066CFF534951775087112139-0:0 -> ../../sde']
        ]

        MBED format
        {
            'mount_point' : <>,
            'serial_port' : <>,
            'target_id' : <>,
            'platform_name' : <>,
        }

        TIDS format
        {
            "1168": "LPC11U68",
            "1549": "LPC1549",
            "1070": "NRF51822",
            "0200": "KL25Z",
            "0220": "KL46Z",
            "0230": "K20D50M",
            "0240": "K64F"
        }
        """
        # We harness information about what is mounted and connected to serial ports
        disk_ids = self.get_dev_by_id('disk')
        serial_ids = self.get_dev_by_id('serial')
        mount_ids = self.get_mounts()

        # Extra data to identify mbeds by target_id
        tids = self.manufacture_ids

        # Listing known and undetected / orphan devices
        mbeds = self.get_detected(tids, disk_ids, serial_ids, mount_ids)
        orphans = self.get_not_detected(tids, disk_ids, serial_ids, mount_ids)
        all_devices = mbeds + orphans

        self.ERRORLEVEL_FLAG = 0

        result = []
        tidhex = re.compile(r'_([0-9a-fA-F]+)-\d+:\d+')
        for device in all_devices:
            tid = None
            m = tidhex.search(device[4])
            if m and len(m.groups()):
                tid = m.group(1)
            mbed = {'mount_point' : device[2],
                    'serial_port' : device[3],
                    'target_id' : tid,
                    'platform_name' : device[0]
            }

            # Deducing mbed-enabled TargetID based on available targetID definition DB.
            # If TargetID from USBID is not recognized we will try to check URL in mbed.htm
            mbed_htm_target_id = self.get_mbed_htm_target_id(device[2]) # device[2] is a 'mount_point'
            if mbed_htm_target_id is not None:
                mbed_htm_target_id_prefix = mbed_htm_target_id[0:4]
                if mbed_htm_target_id_prefix in tids:
                    # We need to update platform_name and corresponding TargetID (not USBID, but from mbed.htm)
                    mbed['platform_name'] = tids[mbed_htm_target_id_prefix]
                    mbed['target_id'] = mbed_htm_target_id
            mbed['target_id_usb_id'] = tid
            mbed['target_id_mbed_htm'] = mbed_htm_target_id
            result.append(mbed)

            if None in mbed:
                self.ERRORLEVEL_FLAG = -1

        return result

    # Private methods

    def get_dev_by_id_cmd(self, subdir):
        """! Calls command line 'ls' to get devices by their ids
        @details Uses Linux shell command: 'ls -oA /dev/disk/by-id/'
        @return tuple(stdout lines, retcode)
        """
        cmd = 'ls -oA /dev/' + subdir + '/by-id/'
        _stdout, _, retval = self.run_cli_process(cmd)
        return (_stdout.splitlines(), retval)

    def get_dev_by_id_process(self, lines, retval):
        """! Remove unnecessary lines from command line output
        """
        result = []
        if not retval:
            for line in lines:
                line = line.rstrip()
                if not line.lower().startswith('total '):    # total 0
                    result.append(line)
                    self.debug(self.get_dev_by_id_process.__name__, line)
        return result

    def get_dev_by_id(self, subdir):
        """! Lists disk devices by id
        @return List of strings from 'ls' command executed in shell
        """
        lines, retval = self.get_dev_by_id_cmd(subdir)
        return self.get_dev_by_id_process(lines, retval)

    def get_mounts(self):
        """! Lists mounted devices with vfat file system (potential mbeds)
        @result Returns list of all mounted vfat devices
        @details Uses Linux shell command: 'mount | grep vfat'
        """
        result = []
        cmd = 'mount | grep vfat'

        self.debug(self.get_mounts.__name__, cmd)

        _stdout, _, retval = self.run_cli_process(cmd)

        if not retval:
            for line in _stdout.splitlines():
                line = line.rstrip()
                result.append(line)
                self.debug(self.get_mounts.__name__, line)
        return result

    def get_disk_hex_ids(self, disk_list):
        """! Get only hexadecimal IDs for mbed disks
        @param disk_list List of disks in a system with USBID decoration
        @return Returns map of disks and corresponding disks' Hex ids
        @details Uses regular expressions to get Hex strings (TargeTIDs) from list of disks
        """
        disk_hex_ids = {}
        for dl in disk_list:
            m = self.nlp.search(dl)
            if m and len(m.groups()):
                disk_link = m.group(1)
                m = self.hup.search(disk_link)
                if m and len(m.groups()):
                    disk_hex_ids[m.group(1)] = disk_link
        return disk_hex_ids

    def get_mbed_serial(self, serial_list, dhi):
        """! Get mbed serial by unique hex id (dhi) in disk name
        @param serial_list List of all serial ports
        @param dhi Unique Hex id of possible mbed device
        @return Returns None if corresponding serial device is not found, else returns serial device path
        @details Devices are located in Linux '/dev/' directory structure
        """
        for sl in serial_list:
            if dhi in sl:
                m = self.nlp.search(sl)
                if m and len(m.groups()):
                    serial_link = m.group(1)
                    mbed_dev_serial = "/dev/" + self.get_dev_name(serial_link)
                    return mbed_dev_serial
        return None

    def get_detected(self, tids, disk_list, serial_list, mount_list):
        """! Find all known mbed devices and assign name by targetID
        @param tids TargetID comprehensive list for detection (manufacturers_ids)
        @param disk_list List of disks (mount points in /dev/disk)
        @param serial_list List of serial devices (serial ports in /dev/serial)
        @param mount_list List of lines from 'mount' command
        @return list of lists [mbed_name, mbed_dev_disk, mbed_mount_point, mbed_dev_serial, disk_hex_id]
        @details Find for all disk connected all MBED ones we know about from TID list
        """
        # Find for all disk connected all MBED ones we know about from TID list
        disk_hex_ids = self.get_disk_hex_ids(disk_list)
        map_tid_to_mbed = self.get_tid_mbed_name_remap(tids)

        result = []

        # Search if we have
        for dhi in disk_hex_ids.keys():
            for mttm in map_tid_to_mbed.keys():
                if dhi.startswith(mttm):
                    mbed_name = map_tid_to_mbed[mttm]
                    mbed_dev_disk = ""
                    mbed_dev_serial = ""

                    disk_link = disk_hex_ids[dhi]
                    # print "Fount MBED disk: " + disk_link #mbed_name + ": " + mttm + " (" + dhi + ")"
                    mbed_dev_disk = self.get_dev_name(disk_link) # m.group(1) if m and len(m.groups()) else "unknown"
                    mbed_dev_serial = self.get_mbed_serial(serial_list, dhi)
                    # Print detected device
                    mbed_mount_point = self.get_mount_point(mbed_dev_disk, mount_list)
                    if mbed_mount_point:
                        result.append([mbed_name, mbed_dev_disk, mbed_mount_point, mbed_dev_serial, disk_hex_ids[dhi]])
        return result

    def get_not_detected(self, tids, disk_list, serial_list, mount_list):
        """! Find all unknown mbed-enabled devices (may have 'mbed' string in USBID name)
        @param tids TargetID comprehensive list for detection (manufacturers_ids)
        @param disk_list List of disks (mount points in /dev/disk)
        @param serial_list List of serial devices (serial ports in /dev/serial)
        @param mount_list List of lines from 'mount' command
        @return list of lists [mbed_name, mbed_dev_disk, mbed_mount_point, mbed_dev_serial, disk_hex_id]
        @details Find for all disk connected all MBED ones we know about from TID list
        """
        disk_hex_ids = self.get_disk_hex_ids(disk_list)

        map_tid_to_mbed = self.get_tid_mbed_name_remap(tids)
        orphan_mbeds = {}
        for disk in disk_hex_ids:
            if "mbed" in disk_hex_ids[disk].lower():
                orphan_found = True
                for tid in map_tid_to_mbed.keys():
                    if disk.startswith(tid):
                        orphan_found = False
                        break
                if orphan_found:
                    orphan_mbeds[disk] = disk_hex_ids[disk]

        # Search for corresponding MBED serial
        result = []
        # Find orphan serial name
        for dhi in orphan_mbeds:
            orphan_serial = self.get_mbed_serial(serial_list, dhi)
            orphan_dev_disk = self.get_dev_name(disk_hex_ids[dhi])
            orphan_dev_serial = '/dev/' + self.get_dev_name(orphan_serial) if orphan_serial else None
            orphan_mount_point = self.get_mount_point(orphan_dev_disk, mount_list)
            if orphan_mount_point:
                result.append([None, orphan_dev_disk, orphan_mount_point, orphan_dev_serial, disk_hex_ids[dhi]])
        return result

    def get_tid_mbed_name_remap(self, tids):
        """! Remap to get mapping:  ID -> mbed name
        """
        return tids

    def get_dev_name(self, link):
        """! Get device name from symbolic link list
        """
        device_sufix_pattern = ".*/([a-zA-Z0-9]*)$"
        dsp = re.compile(device_sufix_pattern)
        m = dsp.search(link)
        mbed_dev = m.group(1) if m and len(m.groups()) else "unknown"
        return mbed_dev

    def get_mount_point(self, dev_name, mount_list):
        """! Find mount points for MBED devices using mount command output
        @param dev_name Device name (e.g 'sda')
        @param mount_list List of all mounted devices (strings from Linux mount shell command)
        @return Returns None if mount point not found. Else returns device mount path
        @details We want to scan names of mount points like this:
        /media/MBED_xxx
        /media/MBED__xxx
        /media/MBED-xxx
        """
        mount_media_pattern = "^/[a-zA-Z0-9/]*/" + dev_name  + " on (/[a-zA-Z0-9_\-/]*) "
        mmp = re.compile(mount_media_pattern)
        for mount in mount_list:
            m = mmp.search(mount)
            if m and len(m.groups()):
                return m.group(1)
        return None
