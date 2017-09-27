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

def _find_TTY(obj):
    ''' Find the first tty (AKA IODialinDevice) that we can find in the
        children of the specified object, or None if no tty is present.
    '''
    if 'IODialinDevice' in obj:
        return obj['IODialinDevice']
    if 'IORegistryEntryChildren' in obj:
        for child in obj['IORegistryEntryChildren']:
            found = _find_TTY(child)
            if found:
                return found
    return None

class MbedLsToolsDarwin(MbedLsToolsBase):
    """ mbed-enabled platform detection on Mac OS X
    """

    def __init__(self, **kwargs):
        MbedLsToolsBase.__init__(self, **kwargs)
        self.mbed_volume_name_match = re.compile(r'(\bmbed\b|\bSEGGER MSD\b)',
                                                 re.I)
        self.mac_version = float('.'.join(platform.mac_ver()[0].split('.')[:2]))

    def find_candidates(self):
        # {volume_id: {serial:, vendor_id:, product_id:, tty:}}
        volumes = self._volumes()

        # {volume_id: mount_point}
        mounts = self._mount_points()
        return [
            {
                'mount_point': mounts[v],
                'serial_port': volumes[v]['tty'],
                'target_id_usb_id': volumes[v].get('serial')
            } for v in set(volumes.keys()) and set(mounts.keys())
        ]

    def _mount_points(self):
        ''' Returns map {volume_id: mount_point} '''
        diskutil_ls = subprocess.Popen(['diskutil', 'list', '-plist'], stdout=subprocess.PIPE)
        diskutil_ls.wait()
        disks = plistlib.readPlist(diskutil_ls.stdout)

        return {disk['DeviceIdentifier']: disk.get('MountPoint', None)
                for disk in disks['AllDisksAndPartitions']}

    def _volumes(self):
        ''' returns a map {volume_id: {serial:, vendor_id:, product_id:, tty:}'''

        # to find all the possible mbed volumes, we look for registry entries
        # under all possible USB tree which have a "BSD Name" that starts with
        # "disk" # (i.e. this is a USB disk), and have a IORegistryEntryName that
        # matches /\cmbed/
        # Once we've found a disk, we can search up for a parent with a valid
        # serial number, and then search down again to find a tty that's part
        # of the same composite device
        # ioreg -a -r -n <usb_controller_name> -l
        usb_controllers = ['AppleUSBXHCI', 'AppleUSBUHCI', 'AppleUSBEHCI',
                           'AppleUSBOHCI', 'IOUSBHostDevice']

        cmp_par = '-n'
        # For El Captain we need to list all the instances of (-c) rather than
        # compare names (-n)
        if self.mac_version >= 10.11:
            cmp_par = '-c'

        for usb_controller in usb_controllers:
            ioreg_usb = subprocess.Popen(['ioreg', '-a', '-r', cmp_par, usb_controller, '-l'], stdout=subprocess.PIPE)
            ioreg_usb.wait()
            try:
                usb_tree = plistlib.readPlist(ioreg_usb.stdout)
            except:
                usb_tree = []

        r = {}

        def findVolumesRecursive(obj, parents):
            if  ('BSD Name' in obj and obj['BSD Name'].startswith('disk') and
                 self.mbed_volume_name_match.search(obj['IORegistryEntryName'])):
                disk_id = obj['BSD Name']
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
                        usb_info['tty'] = _find_TTY(parent)
                        break
                r[disk_id] = usb_info
            if 'IORegistryEntryChildren' in obj:
                for child in obj['IORegistryEntryChildren']:
                    findVolumesRecursive(child, [obj] + parents)

        for obj in usb_tree:
            findVolumesRecursive(obj, [])

        return r
