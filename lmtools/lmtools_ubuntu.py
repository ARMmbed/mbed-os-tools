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
import subprocess

from lmtools_base import LmToolsBase


class LmToolsUbuntu(LmToolsBase):
    """ LmToolsUbuntu supports mbed enabled platforms detection across Debian/Ubuntu OS family
    """
    def __init__(self):
        """ ctor
        """
        LmToolsBase.__init__(self)
        self.os_supported.append('Ubuntu')
        self.hex_uuid_pattern = "usb-[0-9a-zA-Z_-]*_([0-9a-zA-Z]*)-.*"
        self.name_link_pattern = "(usb-[0-9a-zA-Z_-]*_[0-9a-zA-Z]*-.*$)"
        self.mount_media_pattern = "^/[a-zA-Z0-9/]* on (/[a-zA-Z0-9/]*) "

    def list_mbeds(self):
        """ Function returns mbed list with platform names if possible
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

        result = []
        tidhex = re.compile(r'_([0-9a-fA-F]+)')
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
            result.append(mbed)
        return result

    # Private methods

    def get_dev_by_id(self, subdir):
        """ Lists disk devices by id
            Command: 'ls -oA /dev/disk/by-id/'
        """
        result = []
        cmd = 'ls -oA /dev/' + subdir + '/by-id/'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            # print line,
            result.append(line)
        retval = p.wait()
        return result

    def get_mounts(self):
        """ Lists mounted devices with vfat file system (potential mbeds)
        """
        result = []
        cmd = 'mount | grep vfat'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            # print line,
            result.append(line)
        retval = p.wait()
        return result

    def get_disk_hex_ids(self, disk_list):
        """ Get only hexadecimal IDs for mbed disks
        """
        nlp = re.compile(self.name_link_pattern)
        hup = re.compile(self.hex_uuid_pattern)
        disk_hex_ids = {}
        for dl in disk_list:
            m = nlp.search(dl)
            if m and len(m.groups()):
                disk_link = m.group(1)
                m = hup.search(disk_link)
                if m and len(m.groups()):
                    disk_hex_ids[m.group(1)] = disk_link
        return disk_hex_ids

    def get_mbed_serial(self, serial_list, dhi):
        """ Get mbed serial by unique hex id (dhi) in disk name  """
        nlp = re.compile(self.name_link_pattern)
        for sl in serial_list:
            if dhi in sl:
                m = nlp.search(sl)
                if m and len(m.groups()):
                    serial_link = m.group(1)
                    mbed_dev_serial = "/dev/" + self.get_dev_name(serial_link)
                    return mbed_dev_serial
        return None

    def get_detected(self, tids, disk_list, serial_list, mount_list):
        """ Find all known mbed devices
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
                    if mbed_mount_point and  mbed_dev_serial:
                        result.append([mbed_name, mbed_dev_disk, mbed_mount_point, mbed_dev_serial, disk_hex_ids[dhi]])
        return result

    def get_not_detected(self, tids, disk_list, serial_list, mount_list):
        """ Find all unknown mbed enabled devices
        """
        map_tid_to_mbed = self.get_tid_mbed_name_remap(tids)
        orphan_mbeds = []
        for disk in disk_list:
            if "mbed" in disk.lower():
                orphan_found = True
                for tid in map_tid_to_mbed.keys():
                    if tid in disk:
                        orphan_found = False
                        break
                if orphan_found:
                    orphan_mbeds.append(disk)

        # Search for corresponding MBED serial
        disk_hex_ids = self.get_disk_hex_ids(orphan_mbeds)

        result = []
        # FInd orphan serial name
        for dhi in disk_hex_ids:
            orphan_serial = self.get_mbed_serial(serial_list, dhi)
            if orphan_serial:
                orphan_dev_disk = self.get_dev_name(disk_hex_ids[dhi])
                orphan_dev_serial = '/dev/' + self.get_dev_name(orphan_serial)
                orphan_mount_point = self.get_mount_point(orphan_dev_disk, mount_list)
                if orphan_mount_point and orphan_dev_serial:
                    result.append([None, orphan_dev_disk, orphan_mount_point, orphan_dev_serial, disk_hex_ids[dhi]])
        return result

    def get_tid_mbed_name_remap(self, tids):
        """ Remap to get mapping:  ID -> mbed name
        """
        return tids

    def get_dev_name(self, link):
        """ Get device name from symbolic link list
        """
        device_sufix_pattern = ".*/([a-zA-Z0-9]*)$"
        dsp = re.compile(device_sufix_pattern)
        m = dsp.search(link)
        mbed_dev = m.group(1) if m and len(m.groups()) else "unknown"
        return mbed_dev

    def get_mount_point(self, dev_name, mount_list):
        """ Find mount points for MBED devices using mount command output  """
        mount_media_pattern = "^/[a-zA-Z0-9/]*/" + dev_name  + " on (/[a-zA-Z0-9/]*) "
        mmp = re.compile(mount_media_pattern)
        for mount in mount_list:
            m = mmp.search(mount)
            if m and len(m.groups()):
                return m.group(1)
        return None
