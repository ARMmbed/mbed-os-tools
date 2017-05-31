"""
mbed SDK
Copyright (c) 2011-2016 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""

import json
import os
import mbed_lstools
from time import sleep
from mbed_host_tests import DEFAULT_BAUD_RATE
from sets import Set
import mbed_host_tests.host_tests_plugins as ht_plugins


class Mbed:
    """! Base class for a host driven test
    @details This class stores information about things like disk, port, serial speed etc.
             Class is also responsible for manipulation of serial port between host and mbed device
    """
    def __init__(self, options):
        """ ctor
        """
        # For compatibility with old mbed. We can use command line options for Mbed object
        # or we can pass options directly from .
        self.options = options

        # Options related to copy / reset mbed device
        self.port = self.options.port
        self.disk = self.options.disk
        self.target_id = self.options.target_id
        self.image_path = self.options.image_path.strip('"') if self.options.image_path is not None else ''
        self.copy_method = self.options.copy_method
        self.program_cycle_s = float(self.options.program_cycle_s if self.options.program_cycle_s is not None else 2.0)
        self.polling_timeout = self.options.polling_timeout

        # Serial port settings
        self.serial_baud = DEFAULT_BAUD_RATE
        self.serial_timeout = 1

        # Users can use command to pass port speeds together with port name. E.g. COM4:115200:1
        # Format if PORT:SPEED:TIMEOUT
        port_config = self.port.split(':') if self.port else ''
        if len(port_config) == 2:
            # -p COM4:115200
            self.port = port_config[0]
            self.serial_baud = int(port_config[1])
        elif len(port_config) == 3:
            # -p COM4:115200:0.5
            self.port = port_config[0]
            self.serial_baud = int(port_config[1])
            self.serial_timeout = float(port_config[2])

        # Overriding baud rate value with command line specified value
        self.serial_baud = self.options.baud_rate if self.options.baud_rate else self.serial_baud

        # Test configuration in JSON format
        self.test_cfg = None
        if self.options.json_test_configuration is not None:
            # We need to normalize path before we open file
            json_test_configuration_path = self.options.json_test_configuration.strip("\"'")
            try:
                print "MBED: Loading test configuration from '%s'..." % json_test_configuration_path
                with open(json_test_configuration_path) as data_file:
                    self.test_cfg = json.load(data_file)
            except IOError as e:
                print "MBED: Test configuration JSON file '{0}' I/O error({1}): {2}".format(json_test_configuration_path, e.errno, e.strerror)
            except:
                print "MBED: Test configuration JSON Unexpected error:", str(e)
                raise

    def copy_image(self, image_path=None, disk=None, copy_method=None, port=None):
        """! Closure for copy_image_raw() method.
        @return Returns result from copy plugin
        """

        def get_remount_count(disk_path, tries=2):
            for cur_try in range(1, tries + 1):
                try:
                    files_on_disk = [x.upper() for x in os.listdir(disk_path)]
                    print "Files on disk %s"% (files_on_disk)
                    if 'DETAILS.TXT' in files_on_disk:
                        with open(os.path.join(disk_path, 'DETAILS.TXT'), 'r') as details_txt:
                            for line in details_txt.readlines():
                                if 'Remount count:' in line:
                                    return int(line.replace('Remount count: ', ''))
                except OSError as e:
                    print 'Failed to get remount count due to OSError. ' \
                          'Retrying in 1 second (try %s of %s)' % (cur_try, tries)
                    print e
                    sleep(1)

        # Set-up closure environment
        if not image_path:
            image_path = self.image_path
        if not disk:
            disk = self.disk
        if not copy_method:
            copy_method = self.copy_method
        if not port:
            port = self.port

        target_id = self.target_id
        initial_remount_count = get_remount_count(disk)
        # Call proper copy method
        result = self.copy_image_raw(image_path, disk, copy_method, port)
        sleep(self.program_cycle_s)

        if target_id:
            bad_files = Set(['ASSERT.TXT', 'FAIL.TXT'])

            # Re-try at max 5 times with 0.5 sec in delay
            for i in range(5):
                # mbed_lstools.create() should be done inside the loop. Otherwise it will loop on same data.
                mbeds = mbed_lstools.create()
                mbeds_by_tid = mbeds.list_mbeds_by_targetid()   # key: target_id, value mbedls_dict()
                if target_id in mbeds_by_tid:
                    if 'mount_point' in mbeds_by_tid[target_id] and mbeds_by_tid[target_id]['mount_point']:
                        if not initial_remount_count is None:
                            new_remount_count = get_remount_count(disk)
                            if not new_remount_count is None and new_remount_count == initial_remount_count:
                                sleep(0.5)
                                continue

                        common_items = []
                        try:
                            items = Set([x.upper() for x in os.listdir(mbeds_by_tid[target_id]['mount_point'])])
                            common_items = bad_files.intersection(items)
                        except OSError as e:
                            print "Failed to enumerate disk files, retrying"
                            continue

                        for common_item in common_items:
                            full_path = os.path.join(mbeds_by_tid[target_id]['mount_point'], common_item)
                            print "FS_ERROR: Found %s"% (full_path)
                            bad_file_contents = "[failed to read bad file]"
                            try:
                                with open(full_path, "r") as bad_file:
                                    bad_file_contents = bad_file.read()
                            except IOError as error:
                                print "ERROR opening '%s': %s" % (full_path, error)
                            print "FS_ERROR: Contents\n%s"% (bad_file_contents)
                            if common_item != 'FAIL.TXT':
                                try:
                                    os.remove(full_path)
                                except OSError as error:
                                    print "ERROR removing '%s': %s" % (full_path, error)
                        if common_items:
                            result = False
                            if 'ASSERT.TXT' in common_items:
                                raise Exception('ASSERT.TXT found!')
                        break
                sleep(0.5)
        
        return result

    def copy_image_raw(self, image_path=None, disk=None, copy_method=None, port=None):
        """! Copy file depending on method you want to use. Handles exception
             and return code from shell copy commands.
        @return Returns result from copy plugin
        @details Method which is actually copying image to mbed
        """
        # image_path - Where is binary with target's firmware

        # Select copy_method
        # We override 'default' method with 'shell' method
        copy_method = {
            None : 'shell',
            'default' : 'shell',
        }.get(copy_method, copy_method)

        result = ht_plugins.call_plugin('CopyMethod',
                                        copy_method,
                                        image_path=image_path,
                                        serial=port,
                                        destination_disk=disk,
                                        target_id=self.target_id,
                                        pooling_timeout=self.polling_timeout)
        return result

    def hw_reset(self):
        """
        Performs hardware reset of target ned device.

        :return:
        """
        device_info = {}
        result = ht_plugins.call_plugin('ResetMethod',
                                        'power_cycle',
                                        target_id=self.target_id,
                                        device_info=device_info)
        if result:
            self.port = device_info['serial_port']
            self.disk = device_info['mount_point']
        return result

