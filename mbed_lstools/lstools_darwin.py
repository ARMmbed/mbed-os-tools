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
import subprocess
import plistlib
import platform

from .lstools_base import MbedLsToolsBase

import logging

logger = logging.getLogger("mbedls.lstools_darwin")

class MbedLsToolsDarwin(MbedLsToolsBase):
    """ MbedLsToolsDarwin supports mbed-enabled platforms detection on Mac OS X
    """

    mbed_volume_name_match = re.compile(r'(\bmbed\b|\bSEGGER MSD\b)', re.I)

    def list_mbeds(self):
        """ returns mbed list with platform names if possible
        """

        result = []

        # {volume_id: {serial:, vendor_id:, product_id:, tty:}}
        volumes = self.get_mbed_volumes()

        # {volume_id: mount_point}
        mounts = self.get_mount_points()

        volumes_keys = set(volumes.keys())
        mounts_keys = set(mounts.keys())
        intersection = volumes_keys & mounts_keys

        valid_volumes = {}

        for key in intersection:
            valid_volumes[key] = volumes[key]

        # put together all of that info into the expected format:
        result =  [
            {
                'mount_point': mounts[v],
                'serial_port': volumes[v]['tty'],
                  'target_id': self.target_id(volumes[v]),
              'platform_name': self.platform_name(self.target_id(volumes[v]))
            } for v in valid_volumes
        ]

        self.ERRORLEVEL_FLAG = 0

        # if we're missing any platform names, try to fill those in by reading
        # mbed.htm:
        for i, _ in enumerate(result):
            if None in result[i]:
                self.ERRORLEVEL_FLAG = -1
                continue

            if result[i]['mount_point']:
                # Deducing mbed-enabled TargetID based on available targetID definition DB.
                # If TargetID from USBID is not recognized we will try to check URL in mbed.htm
                htm_target_id = self.get_mbed_htm_target_id(result[i]['mount_point'])
                if htm_target_id:
                    result[i]['target_id_usb_id'] = result[i]['target_id']
                    result[i]['target_id'] = htm_target_id
                    result[i]['platform_name'] = self.platform_name(htm_target_id[:4])
                result[i]['target_id_mbed_htm'] = htm_target_id

        return result


    def get_mount_points(self):
        ''' Returns map {volume_id: mount_point} '''

        # list disks, this gives us disk name, and volume name + mount point:
        diskutil_ls = subprocess.Popen(['diskutil', 'list', '-plist'], stdout=subprocess.PIPE)
        disks = plistlib.readPlist(diskutil_ls.stdout)
        diskutil_ls.wait()

        r = {}

        for disk in disks['AllDisksAndPartitions']:
            mount_point = None
            if 'MountPoint' in disk:
                mount_point = disk['MountPoint']
            r[disk['DeviceIdentifier']] = mount_point

        return r


    def get_mbed_volumes(self):
        ''' returns a map {volume_id: {serial:, vendor_id:, product_id:, tty:}'''

        # to find all the possible mbed volumes, we look for registry entries
        # under all possible USB bus which have a "BSD Name" that starts with "disk"
        # (i.e. this is a USB disk), and have a IORegistryEntryName that
        # matches /\cmbed/
        # Once we've found a disk, we can search up for a parent with a valid
        # serial number, and then search down again to find a tty that's part
        # of the same composite device
        # ioreg -a -r -n <usb_controller_name> -l
        usb_controllers = ['AppleUSBXHCI', 'AppleUSBUHCI', 'AppleUSBEHCI', 'AppleUSBOHCI', 'IOUSBHostDevice']
        usb_bus = []

        cmp_par = '-n'
        # For El Captain we need to list all the instances of (-c) rather than compare names (-n)
        mac_ver = float('.'.join(platform.mac_ver()[0].split('.')[:2])) # Returns mac version as float XX.YY
        if mac_ver >= 10.11:
            cmp_par = '-c'

        for usb_controller in usb_controllers:
            ioreg_usb = subprocess.Popen(['ioreg', '-a', '-r', cmp_par, usb_controller, '-l'], stdout=subprocess.PIPE)
            try:
                usb_bus = usb_bus + plistlib.readPlist(ioreg_usb.stdout)
            except:
                # Catch when no output is returned from ioreg command
                pass

            ioreg_usb.wait()

        r = {}

        def findTTYRecursive(obj):
            ''' return the first tty (AKA IODialinDevice) that we can find in the
                children of the specified object, or None if no tty is present.
            '''
            if 'IODialinDevice' in obj:
                return obj['IODialinDevice']
            if 'IORegistryEntryChildren' in obj:
                for child in obj['IORegistryEntryChildren']:
                    found = findTTYRecursive(child)
                    if found:
                        return found
            return None

        def findVolumesRecursive(obj, parents):
            if 'BSD Name' in obj and obj['BSD Name'].startswith('disk') and \
                    self.mbed_volume_name_match.search(obj['IORegistryEntryName']):
                disk_id = obj['BSD Name']
                # now search up through our parents until we find a serial number:
                usb_info = {
                        'serial':None,
                     'vendor_id':None,
                    'product_id':None,
                           'tty':None,
                }
                for parent in [obj] + parents:
                    if 'USB Serial Number' in parent:
                        usb_info['serial'] = parent['USB Serial Number']
                    if 'idVendor' in parent and 'idProduct' in parent:
                        usb_info['vendor_id'] = parent['idVendor']
                        usb_info['product_id'] = parent['idProduct']
                    if usb_info['serial']:
                        # stop at the first one we find (or we'll pick up hubs,
                        # etc.), but first check for a tty that's also a child of
                        # this device:
                        usb_info['tty'] = findTTYRecursive(parent)
                        break
                r[disk_id] = usb_info
            if 'IORegistryEntryChildren' in obj:
                for child in obj['IORegistryEntryChildren']:
                    findVolumesRecursive(child, [obj] + parents)

        for obj in usb_bus:
            findVolumesRecursive(obj, [])

        return r


    def target_id(self, usb_info):
        if usb_info['serial'] is not None:
            return usb_info['serial']
        else:
            return None

    def platform_name(self, target_id):
        return self.plat_db.get(target_id, None)
