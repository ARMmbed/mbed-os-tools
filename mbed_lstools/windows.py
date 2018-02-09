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
import itertools

from .lstools_base import MbedLsToolsBase

import logging
logger = logging.getLogger("mbedls.lstools_win7")
DEBUG = logging.DEBUG
del logging

if sys.version_info[0] < 3:
    import _winreg as winreg
else:
    import winreg

def _composite_device_key(device):
    """! Given two composite devices, return a ranking on its specificity
    @return if no mount_point, then always 0. If mount_point but no serial_port,
    return 1. If mount_point and serial_port, add the prefix_index.
    """
    rank = 0

    if 'mount_point' in device:
        rank += 1
        if device['serial_port'] is not None:
            rank += device['prefix_index']

    return rank


class MbedLsToolsWin7(MbedLsToolsBase):
    """ mbed-enabled platform detection for Windows
    """

    _COMPOSITE_USB_SERVICES = ['usbccgp', 'mbedComposite']

    def __init__(self, **kwargs):
        MbedLsToolsBase.__init__(self, **kwargs)
        self.os_supported.append('Windows7')


    def find_candidates(self):
        result = []
        composite_devices = self._get_composite_devices()
        if composite_devices:
            volumes = self._get_volumes()
            for composite_device in composite_devices:
                tid = composite_device['target_id_usb_id']
                found_index = None
                for index, volume in enumerate(volumes):
                    if volume['target_id_usb_id'] == tid:
                        found_index = index
                        composite_device.update(volume)
                        result.append(composite_device)

                if found_index is not None:
                    volumes.pop(found_index)
        return result


    def _get_volumes(self):
        """! Get the volumes present on the system
        @return List of mount points and their associated target id
          Ex. [{ 'mount_point': 'D:', 'target_id_usb_id': 'xxxx'}, ...]
        """
        result = []
        try:
            # Open the registry key for mounted devices
            mounted_devices_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                'SYSTEM\\MountedDevices')
            for v in self.iter_vals(mounted_devices_key):
                # Valid entries have the following format: \DosDevices\D:
                if 'DosDevices' in v[0]:
                    entry_string = v[1].decode('utf-16le', 'ignore')
                    mount_point_match = re.match('.*\\\\(.:)$', v[0])

                    if not mount_point_match:
                        logger.debug('Invalid disk pattern for entry %s, skipping' % v[0])
                        continue

                    mount_point = mount_point_match.group(1)
                    logger.debug('Mount point %s found for volume %s' % (mount_point,
                        entry_string))

                    # TargetID is a hex string with 10-48 chars
                    target_id_match = re.search('[&#]([0-9A-Za-z]{10,48})[&#]', entry_string)
                    if not target_id_match:
                        logger.debug('Entry %s has invalid target id pattern '
                            '%s, skipping' % (v[0], entry_string))
                        continue

                    target_id = target_id_match.group(1)
                    logger.debug('Target ID %s found for volume %s' % (target_id,
                        entry_string))

                    result.append({
                        'mount_point': mount_point,
                        'target_id_usb_id': target_id
                    })
        except OSError:
            logger.error('Failed to open "MountedDevices" in registry')

        return result


    def _get_composite_devices(self):
        """! Get connected composite USB devices
        @return List of target ids and serial properties
          Ex. [{ 'target_id_usb_id': 'xxxx', 'serial_port': 'COMxx', 'mount_point': None }, ...]
        @details The composite devices are required to have a mass storage device.
            If a mass storage is present, a key of 'mount_point' should be returned
            with a value of None (to be completed later)
        """

        result = []

        # Open the root registry key
        try:
            control_set_key_string = "SYSTEM\\CurrentControlSet"
            control_set_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                control_set_key_string)
        except OSError:
            logger.error('Could not find "%s" in registry' % control_set_key_string)
            return []

        # Enumerate all USB VID/PID pairs
        try:
            vid_pid_key = winreg.OpenKey(control_set_key, 'Enum\\USB')
            vid_pid_keys = list(self.iter_keys_as_str(vid_pid_key))
        except OSError:
            logger.error('Could not enumerate USB VID/PID pairs')
            return []

        # Find all composite USB services
        found_composite_keys = []
        for usb_service in self._COMPOSITE_USB_SERVICES:
            try:
                found_composite_keys.append(winreg.OpenKey(control_set_key,
                    'Services\\%s\\Enum' % usb_service))
            except OSError:
                logger.debug('Composite USB service "%s" not found' % usb_service)

        # Find all enumerated composite USB devices
        composite_iter_vals = [self.iter_vals(k) for k in found_composite_keys]
        for point, label, _ in itertools.chain.from_iterable(composite_iter_vals):
            try:
                # These keys in the registry enumerate all composite DosDevices
                # as a value with an integer. This check ensures we ignore a few
                # helper values in the registry key.
                _ = int(point)
            except ValueError:
                continue

            label_parts = label.split('\\')

            # The expected format is "USB\VID_XXXX&PID_XXXX\<target id>"
            if len(label_parts) != 3:
                logger.debug('Unrecognized device path %s' % label)
                continue

            if label_parts[0] != 'USB':
                logger.debug('Expected device to be under "USB", '
                    'actual location was "%s"' % label_parts[0])
                continue

            vid_pid_prefix = label_parts[1]
            target_id_usb_id = label_parts[2]

            device = {}

            try:
                composite_key_string = '%s\\%s' % (vid_pid_prefix, target_id_usb_id)
                logger.debug('Composite device at key %s' % composite_key_string)
                composite_key = winreg.OpenKey(vid_pid_key, composite_key_string)
                # Order is important here. We should default to using the
                # target_id_usb_id here but fallback to the ParentIdPrefix
                parent_id_prefixes = [target_id_usb_id]
                try:
                    composite_parent_id_prefix, _ = winreg.QueryValueEx(composite_key,
                        'ParentIdPrefix')
                    parent_id_prefixes.append(composite_parent_id_prefix)
                except OSError:
                    logger.debug('No ParentIdPrefix found')

                vid_pid_matches = [
                    m for m in vid_pid_keys
                    if m.startswith(vid_pid_prefix) and m != vid_pid_prefix
                ]

                options = []

                for prefix_index, parent_id_prefix in enumerate(parent_id_prefixes):
                    device = {
                        'target_id_usb_id': target_id_usb_id,
                        'serial_port': None,
                        'prefix_index': len(parent_id_prefixes) - prefix_index
                    }

                    for vid_pid_match in vid_pid_matches:
                        logger.debug('Endpoint parent at key %s' % vid_pid_match)
                        endpoint_parent_key = winreg.OpenKey(vid_pid_key, vid_pid_match)

                        candidates = [
                            c for c in list(self.iter_keys_as_str(endpoint_parent_key))
                            if any(c.startswith(parent_id_prefix) for p in parent_id_prefixes)
                        ]

                        if len(candidates) == 0:
                            logger.debug('No candidate found for parent_id_prefix'
                                ' %s' % parent_id_prefix)
                            break
                        elif len(candidates) > 1:
                            logger.debug('Unexpectedly found two candidates %s' % candidates)
                            logger.debug('Picking %s and continuing' % candidates[0])

                        endpoint_key_string = '%s\\%s' % (vid_pid_match, candidates[0])
                        logger.debug('Endpoint at key %s' % endpoint_key_string)
                        endpoint_key = winreg.OpenKey(vid_pid_key, endpoint_key_string)
                        # This verifies that a USB Storage device is associated with
                        # the composite device
                        if not 'mount_point' in device:
                            try:
                                service, _ = winreg.QueryValueEx(endpoint_key, 'Service')
                                if service.upper() == 'USBSTOR':
                                    device['mount_point'] = None
                                    continue
                            except OSError:
                                pass

                        # This adds the serial port information for the device if
                        # it is availble
                        if device['serial_port'] is None:
                            try:
                                device_parameters_key = winreg.OpenKey(endpoint_key,
                                    'Device Parameters')
                                device['serial_port'], _ = winreg.QueryValueEx(
                                    device_parameters_key, 'PortName')
                                continue
                            except OSError:
                                pass

                    options.append(device)

            except OSError as e:
                logger.debug('Skipping device entry %s, %s' % (label, e))
                continue

            options.sort(key=_composite_device_key, reverse=True)

            if len(options) == 0:
                logger.debug('No options were found, skipping composite device')
                continue


            device = options[0]
            del device['prefix_index']

            # A target_id_usb_id and mount point must be present to be included
            # in the candidates
            required_keys = set(['target_id_usb_id', 'mount_point'])
            missing_keys = required_keys - set(device.keys())
            if missing_keys:
                logger.debug('Device %s missing keys %s, skipping' % (label,
                    list(missing_keys)))
            else:
                logger.debug('Candidate found %s' % label)
                result.append(device)

        return result


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

    def mount_point_ready(self, path):
        """! Check if a mount point is ready for file operations
        @return Returns True if the given path exists, False otherwise
        @details Calling the Windows command `dir` instead of using the python
        `os.path.exists`. The latter causes a Python error box to appear claiming
        there is "No Disk" for some devices that are in the ejected state. Calling
        `dir` prevents this since it uses the Windows API to determine if the
        device is ready before accessing the file system.
        """
        stdout, stderr, retcode = self._run_cli_process('dir %s' % path)
        result = True if retcode == 0 else False

        if result:
            logger.debug("Mount point %s is ready", path)
        else:
            logger.debug("Mount point %s reported not ready with error '%s'",
                          path, stderr.strip())

        return result
