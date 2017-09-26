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
from os.path import expanduser
import json
from os import listdir
from os.path import isfile, join
import logging

from .platform_database import PlatformDatabase, LOCAL_PLATFORM_DATABASE, \
    LOCAL_MOCKS_DATABASE

logger = logging.getLogger("mbedls.lstools_base")


class MbedLsToolsBase:
    """ Base class for mbed-lstools, defines mbed-ls tools interface for
    mbed-enabled devices detection for various hosts
    """

    # Which OSs are supported by this module
    # Note: more than one OS can be supported by mbed-lstools_* module
    os_supported = []

    # Directory where we will store global (OS user specific mocking)
    HOME_DIR = expanduser("~")
    MOCK_FILE_NAME = '.mbedls-mock'
    RETARGET_FILE_NAME = 'mbedls.json'
    DETAILS_TXT_NAME = 'DETAILS.TXT'
    MBED_HTM_NAME = 'mbed.htm'
    ERRORLEVEL_FLAG = 0

    def __init__(self, **kwargs):
        """ ctor
        """
        self.retarget_data = {}          # Used to retarget mbed-enabled platform properties

        platform_dbs = []
        if isfile(self.MOCK_FILE_NAME) or ("force_mock" in kwargs and kwargs['force_mock']):
            platform_dbs.append(self.MOCK_FILE_NAME)
        elif isfile(LOCAL_MOCKS_DATABASE):
            platform_dbs.append(LOCAL_MOCKS_DATABASE)
        platform_dbs.append(LOCAL_PLATFORM_DATABASE)
        self.plat_db = PlatformDatabase(platform_dbs,
                                        primary_database=platform_dbs[0])

        if 'skip_retarget' not in kwargs or not kwargs['skip_retarget']:
            self.retarget()

    def mock_manufacture_id(self, mid, platform_name, oper='+'):
        """! Replace (or add if manufacture id doesn't exist) entry in self.manufacture_ids
        @param oper '+' add new mock / override existing entry
                    '-' remove mid from mocking entry
        @return Mocked structure (json format)
        """
        if oper is '+':
            self.plat_db.add(mid, platform_name, permanent=True)
        elif oper is '-':
            self.plat_db.remove(mid, permanent=True)
        else:
            raise ValueError("oper can only be [+-]")

    def list_manufacture_ids(self):
        """! Creates list of all available mappings for target_id -> Platform
        @return String with table formatted output
        """
        from prettytable import PrettyTable

        columns = ['target_id_prefix', 'platform_name']
        pt = PrettyTable(columns)
        for col in columns:
            pt.align[col] = 'l'

        for target_id_prefix, platform_name in sorted(self.plat_db.items()):
            pt.add_row([target_id_prefix, platform_name])

        return pt.get_string()

    def retarget_read(self):
        """! Load retarget data from local file
        @return Curent retarget configuration (dictionary)
        """
        if os.path.isfile(self.RETARGET_FILE_NAME):
            logger.debug("reading retarget file %s", self.RETARGET_FILE_NAME)
            try:
                with open(self.RETARGET_FILE_NAME, "r", encoding="utf-8") as f:
                    return json.load(f)
            except IOError as e:
                logger.exception(e)
            except ValueError as e:
                logger.exception(e)
        return {}

    def retarget(self):
        """! Enable retargeting
        @details Read data from local retarget configuration file
        @return Retarget data structure read from configuration file
        """
        self.retarget_data = self.retarget_read()
        return self.retarget_data

    # Note: 'Ven_SEGGER' - This is used to detect devices from EFM family, they use Segger J-LInk to wrap MSD and CDC
    usb_vendor_list = ['Ven_MBED', 'Ven_SEGGER', 'Ven_ARM_V2M']

    # Interface
    def list_mbeds(self):
        """! Get information about mbeds connected to device
        @return Returns None or if no error MBED_BOARDS = [ <MBED_BOARD>, ]
        @details MBED_BOARD
        {
            'mount_point' : <>,
            'serial_port' : <>,
            'target_id' : <>,
            'platform_name' : <>,
            'daplink_version' : <>,
        }
        # If field unknown, place None
        """
        return None

    def list_mbeds_ext(self):
        """! Function adds extra information for each mbed device
        @return Returns list of mbed devices plus extended data like 'platform_name_unique'
        @details Get information about mbeds with extended parameters/info included
        """
        platform_names = {} # Count existing platforms and assign unique number

        mbeds = self.list_mbeds()
        for i, val in enumerate(mbeds):
            platform_name = val['platform_name']
            if platform_name not in platform_names:
                platform_names[platform_name] = 0
            else:
                platform_names[platform_name] += 1
            # Assign normalized, unique string at the end of target name: TARGET_NAME[x] where x is an ordinal integer
            mbeds[i]['platform_name_unique'] = "%s[%d]" % (platform_name, platform_names[platform_name])

            # Retarget values from retarget (mbedls.json) file
            if self.retarget_data and 'target_id' in val:
                target_id = val['target_id']
                if target_id in self.retarget_data:
                    mbeds[i].update(self.retarget_data[target_id])
                    logger.debug("retargeting %s to %s", target_id, mbeds[i])

            # Add interface chip meta data to mbed structure
            details_txt = self.get_details_txt(val['mount_point']) if val['mount_point'] else None
            if details_txt:
                for field in details_txt:
                    field_name = 'daplink_' + field.lower().replace(' ', '_')
                    if field_name not in mbeds[i]:
                        mbeds[i][field_name] = details_txt[field]

            mbed_htm = self.get_mbed_htm(val['mount_point']) if val['mount_point'] else None
            if mbed_htm:
                for field in mbed_htm:
                    field_name = 'daplink_' + field.lower().replace(' ', '_')
                    if field_name not in mbeds[i]:
                        mbeds[i][field_name] = mbed_htm[field]

            logger.debug((mbeds[i]['platform_name_unique'], val['target_id']))
        return mbeds

    def get_dummy_platform(self, platform_name):
        """! Returns simple dummy platform """
        if not hasattr(self, "dummy_counter"):
            self.dummy_counter = {} # platform<str>: counter<int>

        if platform_name not in self.dummy_counter:
            self.dummy_counter[platform_name] = 0

        platform = {
            "platform_name": platform_name,
            "platform_name_unique": "%s[%d]"% (platform_name, self.dummy_counter[platform_name]),
            "mount_point": "DUMMY",
            "serial_port": "DUMMY",
            "target_id": "DUMMY",
            "target_id_mbed_htm": "DUMMY",
            "target_id_usb_id": "DUMMY",
            "daplink_version": "DUMMY"
        }
        self.dummy_counter[platform_name] += 1
        return platform

    def list_platforms(self):
        """! Useful if you just want to know which platforms are currently available on the system
        @return List of (unique values) available platforms
        """
        result = []
        mbeds = self.list_mbeds()
        for i, val in enumerate(mbeds):
            platform_name = str(val['platform_name'])
            if platform_name not in result:
                result.append(platform_name)
        return result

    def list_platforms_ext(self):
        """! Useful if you just want to know how many platforms of each type are currently available on the system
        @return Dict of platform: platform_count
        """
        result = {}
        mbeds = self.list_mbeds()
        for i, val in enumerate(mbeds):
            platform_name = str(val['platform_name'])
            if platform_name not in result:
                result[platform_name] = 1
            else:
                result[platform_name] += 1
        return result

    def list_mbeds_by_targetid(self):
        """! Get information about mbeds with extended parameters/info included
        @return Returns dictionary where keys are TargetIDs and values are mbed structures
        @details Ordered by target id (key: target_id).
        """
        result = {}
        mbed_list = self.list_mbeds_ext()
        for mbed in mbed_list:
            target_id = mbed['target_id']
            result[target_id] = mbed
        return result

    def __str__(self):
        """! Object to string casting

        @return Stringified class object should be prettytable formated string
        """
        return self.get_string()

    def get_string(self, border=False, header=True, padding_width=1, sortby='platform_name'):
        """! Printing with some sql table like decorators
        @param border Table border visibility
        @param header Table header visibility
        @param padding_width Table padding
        @param sortby Column used to sort results
        @return Returns string which can be printed on console
        """
        from prettytable import PrettyTable
        result = ''
        mbeds = self.list_mbeds_ext()
        if mbeds:
            """ ['platform_name', 'mount_point', 'serial_port', 'target_id'] - columns generated from USB auto-detection
                ['platform_name_unique', ...] - columns generated outside detection subsystem (OS dependent detection)
            """
            columns = ['platform_name', 'platform_name_unique', 'mount_point', 'serial_port', 'target_id', 'daplink_version']
            pt = PrettyTable(columns)
            for col in columns:
                pt.align[col] = 'l'

            for mbed in mbeds:
                row = []
                for col in columns:
                    row.append(mbed[col] if col in mbed and mbed[col] else 'unknown')
                pt.add_row(row)
            result = pt.get_string(border=border, header=header, padding_width=padding_width, sortby=sortby)
        return result

    # Private functions supporting API

    def get_json_data_from_file(self, json_spec_filename, verbose=False):
        """! Loads from file JSON formatted string to data structure
        @return None if JSON can be loaded
        """
        result = None
        try:
            with open(json_spec_filename) as data_file:
                try:
                    result = json.load(data_file)
                except ValueError as json_error_msg:
                    result = None
                    logging.error("Parsing file(%s): %s", json_spec_filename, json_error_msg)
        except IOError as fileopen_error_msg:
            logging.warning(fileopen_error_msg)
        return result

    def get_mbed_htm_target_id(self, mount_point):
        """! Function scans mbed.htm to get information about TargetID.
        @param mount_point mbed mount point (disk / drive letter)
        @return Function returns targetID, in case of failure returns None.
        @details Note: This function should be improved to scan variety of boards' mbed.htm files
        """
        result = None
        for line in self.get_mbed_htm_lines(mount_point):
            target_id = self.scan_html_line_for_target_id(line)
            if target_id:
                return target_id
        return result

    def get_mbed_htm_comment_section_ver_build(self, line):
        """! Check for Version and Build date of interface chip firmware im mbed.htm file
        @return (version, build) tuple if successful, None if no info found
        """
        # <!-- Version: 0200 Build: Mar 26 2014 13:22:20 -->
        m = re.search(r'^<!-- Version: (\d+) Build: ([\d\w: ]+) -->', line)
        if m:
            version_str, build_str = m.groups()
            return (version_str.strip(), build_str.strip())

        # <!-- Version: 0219 Build: Feb  2 2016 15:20:54 Git Commit SHA: 0853ba0cdeae2436c52efcba0ba76a6434c200ff Git local mods:No-->
        m = re.search(r'^<!-- Version: (\d+) Build: ([\d\w: ]+) Git Commit SHA', line)
        if m:
            version_str, build_str = m.groups()
            return (version_str.strip(), build_str.strip())

        # <!-- Version: 0.14.3. build 471 -->
        m = re.search(r'^<!-- Version: ([\d+\.]+)\. build (\d+) -->', line)
        if m:
            version_str, build_str = m.groups()
            return (version_str.strip(), build_str.strip())
        return None

    def get_mbed_htm(self, mount_point):
        """! Check for version, build date/timestamp, URL in mbed.htm file
        @param mount_point Where to look for mbed.htm file
        @return Dictoionary with additional DAPlink names
        """
        result = {}
        for line in self.get_mbed_htm_lines(mount_point):
            # Check for Version and Build date of interface chip firmware
            ver_bld = self.get_mbed_htm_comment_section_ver_build(line)
            if ver_bld:
                result['version'], result['build'] = ver_bld

            # Check for mbed URL
            m = re.search(r'url=([\w\d\:/\\\?\.=-_]+)', line)
            if m:
                result['url'] = m.group(1).strip()
        return result

    def get_mbed_htm_lines(self, mount_point):
        result = []
        if mount_point:
            try:
                for mount_point_file in [f for f in listdir(mount_point) if isfile(join(mount_point, f))]:
                    if mount_point_file.lower() == self.MBED_HTM_NAME:
                        mbed_htm_path = os.path.join(mount_point, mount_point_file)
                        try:
                            with open(mbed_htm_path, 'r') as f:
                                result = f.readlines()
                        except IOError:
                            logger.debug('Failed to open file %s', mbed_htm_path)
            except OSError:
                logger.debug('Failed to list mount point %s', mount_point)

        return result

    def get_details_txt(self, mount_point):
        """! Load DETAILS.TXT to dictionary:
            DETAILS.TXT example:
            Version: 0226
            Build:   Aug 24 2015 17:06:30
            Git Commit SHA: 27a236b9fe39c674a703c5c89655fbd26b8e27e1
            Git Local mods: Yes

            or:

            # DAPLink Firmware - see https://mbed.com/daplink
            Unique ID: 0240000029164e45002f0012706e0006f301000097969900
            HIF ID: 97969900
            Auto Reset: 0
            Automation allowed: 0
            Daplink Mode: Interface
            Interface Version: 0240
            Git SHA: c765cbb590f57598756683254ca38b211693ae5e
            Local Mods: 0
            USB Interfaces: MSD, CDC, HID
            Interface CRC: 0x26764ebf
        """
        result = {}
        if mount_point:
            path_to_details_txt = os.path.join(mount_point, self.DETAILS_TXT_NAME)
            if os.path.exists(path_to_details_txt):
                try:
                    with open(path_to_details_txt, 'r') as f:
                        result = self.parse_details_txt(f.readlines())
                except IOError as e:
                    logger.debug('Failed to open file %s: %s', path_to_details_txt, str(e))
        return result if result else None

    def parse_details_txt(self, lines):
        result = {}
        for line in lines:
            if not line.startswith('#'):
                # Lines starting with '#' are comments
                line_split = line.split(':')
                if line_split:
                    idx = line.find(':')
                    result[line_split[0]] = line[idx+1:].strip()

        # Allign with new DAPlink DETAILS.TXT format
        if 'Interface Version' in result:
            result['Version'] = result['Interface Version']
        return result

    def scan_html_line_for_target_id(self, line):
        """! Scan if given line contains target id encoded in URL.
        @return Returns None when no target_id string in line
        """
        # Detecting modern mbed.htm file format
        m = re.search('\?code=([a-fA-F0-9]+)', line)
        if m:
            result = m.groups()[0]
            logger.debug("scan_html_line_for_taget_id %s", line.strip())
            logger.debug("scan_html_line_for_target_id %s %s", m.groups(), result)
            return result
        # Last resort, we can try to see if old mbed.htm format is there
        else:
            m = re.search('\?auth=([a-fA-F0-9]+)', line)
            if m:
                result = m.groups()[0]
                logger.debug("scan_html_line_for_taget_id %s", line.strip())
                logger.debug("scan_html_line_for_target_id %s %s", m.groups(), result)
                return result
        return None

    def mount_point_ready(self, path):
        """! Check if a mount point is ready for file operations
        @return Returns True if the given path exists, False otherwise
        """
        result = os.path.exists(path)

        if result:
            logger.debug("Mount point %s is ready", path)
        else:
            logger.debug("Mount point %s does not exist", path)

        return result

    @staticmethod
    def run_cli_process(cmd, shell=True):
        """! Runs command as a process and return stdout, stderr and ret code
        @param cmd Command to execute
        @return Tuple of (stdout, stderr, returncode)
        """
        from subprocess import Popen, PIPE

        p = Popen(cmd, shell=shell, stdout=PIPE, stderr=PIPE)
        _stdout, _stderr = p.communicate()
        return _stdout, _stderr, p.returncode
