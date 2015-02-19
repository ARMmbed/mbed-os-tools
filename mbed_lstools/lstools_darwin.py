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

from lstools_base import MbedLsToolsBase

class MbedLsToolsDarwin(MbedLsToolsBase):
    """ MbedLsToolsDarwin supports mbed-enabled platforms detection on Mac OS X
    """

    mbed_volume_name_match = re.compile(r'\bmbed\b', re.I)

    def list_mbeds(self):
        """ returns mbed list with platform names if possible
        """
        
        result = []
        
        # {volume_id: mount_point}
        volumes = self.get_mbed_volumes()
        #print "volumes:", volumes
        
        # {volume_id: {serial:, vendor_id:, product_id:}}
        usb_info = self.get_volume_usb_info(volumes.keys())
        #print "usb info:", usb_info

        # {volume_id: tty_path}
        ttys = self.get_serial_ports(usb_info)
        #print "ttys:", ttys

        # put together all of that info into the expected format:
        result =  [
            {
                'mount_point': volumes[v],
                'serial_port': ttys[v],
                  'target_id': self.target_id(usb_info[v]),
              'platform_name': self.platform_name(self.target_id(usb_info[v]))
            } for v in volumes
        ]

        # if we're missing any target ids, try to fill those in by reading
        # mbed.htm:
        for m in result:
            if m['mount_point'] and  not m['target_id']:
                m['target_id'] = self.get_mbed_htm_target_id(m['mount_point'])
        
        # finally fill in any missing platform names:
        for m in result:
            if m['target_id'] and not m['platform_name']:
                tid = m['target_id'][:4]
                m['platform_name'] = self.platform_name(tid)

        return result

    
    def get_mbed_volumes(self):
        ''' Returns map {volume_id: mount_point} '''

        # list disks, this gives us disk name, and volume name + mount point:
        diskutil_ls = subprocess.Popen(['diskutil', 'list', '-plist'], stdout=subprocess.PIPE)
        disks = plistlib.readPlist(diskutil_ls.stdout)
        diskutil_ls.wait()
        
        r = {}

        for disk in disks['AllDisksAndPartitions']:
            if 'VolumeName' in disk and self.mbed_volume_name_match.search(disk['VolumeName']):
                mount_point = None
                if 'MountPoint' in disk:
                    mount_point = disk['MountPoint']
                r[disk['DeviceIdentifier']] = mount_point
        
        return r

    def get_volume_usb_info(self, volumes):
        ''' Returns map {volume_id: {serial:, vendor_id:, product_id:}} '''
        
        # list USB devices, this includes the volume:serial number mapping
        sysprof_usb = subprocess.Popen(['system_profiler', 'SPUSBDataType', '', '-xml'], stdout=subprocess.PIPE)
        usb_devices = plistlib.readPlist(sysprof_usb.stdout)
        sysprof_usb.wait()

        r = {}
            
        # loop over the information, finding any object with
        # {'bsd_name': <volume_id>}, and fetching it's serial_num, product_id
        # and vendor_id fields
        def findVolumesRecursive(obj):
            if 'bsd_name' in obj and obj['bsd_name'] in volumes:
                r[obj['bsd_name']] = {
                        'serial': obj['serial_num'] if 'serial_num' in obj else None,
                     'vendor_id': int(obj['vendor_id'], 16)  if 'vendor_id'  in obj else None,
                    'product_id': int(obj['product_id'], 16) if 'product_id' in obj else None
                }
            if '_items' in obj:
                for child in obj['_items']:
                    findVolumesRecursive(child)

        for obj in usb_devices:
            findVolumesRecursive(obj)

        return r

    def get_serial_ports(self, usb_info):
        ''' Returns map {volume_id: tty_device_file_path} '''
        
        # to find the serial ports associated with a USB device we need to use
        # the wonderful ioreg command. We enumerate the usb bus (list the IO
        # Registry Object Tree rooted at AppleUSBXHCI). Then we can search for
        # anything with a serial number that we know, and search all its child
        # devices for a tty
        # ioreg -a -r -n "AppleUSBXHCI" -l
        ioreg_usb = subprocess.Popen(['ioreg', '-a', '-r', '-n', 'AppleUSBXHCI', '-l'], stdout=subprocess.PIPE)
        usb_bus = plistlib.readPlist(ioreg_usb.stdout)
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


            
        def findDeviceRecursive(obj):
            if 'idProduct' in obj and 'idVendor' in obj:
                pid = obj['idProduct']
                vid = obj['idVendor']
                for volume, info in usb_info.items():
                    if info['product_id'] is not None and info['vendor_id'] is not None and \
                       info['product_id'] == pid      and info['vendor_id'] == vid:
                        tty = findTTYRecursive(obj)
                        # break as soon as we've got something valid
                        if tty:
                            r[volume] = tty
                            return
            if 'IORegistryEntryChildren' in obj:
                for child in obj['IORegistryEntryChildren']:
                    findDeviceRecursive(child)

        for obj in usb_bus:
            findDeviceRecursive(obj)

        return r


    def target_id(self, usb_info):
        if usb_info['serial'] is not None:
            return usb_info['serial'][:4]
        else:
            return None

    def platform_name(self, target_id):
        if target_id in self.manufacture_ids:
            return self.manufacture_ids[target_id[:4]]


