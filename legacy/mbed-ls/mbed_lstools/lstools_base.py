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

import functools
import json
import logging

from mbed_os_tools.detect.lstools_base import (
    FSInteraction,
    MbedDetectLsToolsBase,
)

logger = logging.getLogger("mbedls.lstools_base")
logger.addHandler(logging.NullHandler())

def deprecated(reason):
    """Deprecate a function/method with a decorator"""
    def actual_decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            logger.warning("Call to deprecated function %s. %s",
                        func.__name__, reason)
            return func(*args, **kwargs)
        return new_func
    return actual_decorator

class MbedLsToolsBase(MbedDetectLsToolsBase):
    """ Base class for mbed-lstools, defines mbed-ls tools interface for
    mbed-enabled devices detection for various hosts
    """

    @deprecated("Functionality has been moved into 'list_mbeds'. "
                "Please use list_mbeds with 'unique_names=True' and "
                "'read_details_txt=True'")
    def list_mbeds_ext(self):
        """! Function adds extra information for each mbed device
        @return Returns list of mbed devices plus extended data like 'platform_name_unique'
        @details Get information about mbeds with extended parameters/info included
        """

        return self.list_mbeds(unique_names=True, read_details_txt=True)

    @deprecated("List formatting methods are deprecated for a simpler API. "
                "Please use 'list_mbeds' instead.")
    def list_manufacture_ids(self):
        """! Creates list of all available mappings for target_id -> Platform
        @return String with table formatted output
        """
        from prettytable import PrettyTable, HEADER

        columns = ['target_id_prefix', 'platform_name']
        pt = PrettyTable(columns, junction_char="|", hrules=HEADER)
        for col in columns:
            pt.align[col] = 'l'

        for target_id_prefix, platform_name in sorted(self.plat_db.items()):
            pt.add_row([target_id_prefix, platform_name])

        return pt.get_string()

    @deprecated("List formatting methods are deprecated to simplify the API. "
                "Please use 'list_mbeds' instead.")
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

    @deprecated("List formatting methods are deprecated to simplify the API. "
                "Please use 'list_mbeds' instead.")
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

    @deprecated("List formatting methods are deprecated to simplify the API. "
                "Please use 'list_mbeds' instead.")
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

    @deprecated("List formatting methods are deprecated to simplify the API. "
                "Please use 'list_mbeds' instead.")
    def get_string(self, border=False, header=True, padding_width=1, sortby='platform_name'):
        """! Printing with some sql table like decorators
        @param border Table border visibility
        @param header Table header visibility
        @param padding_width Table padding
        @param sortby Column used to sort results
        @return Returns string which can be printed on console
        """
        from prettytable import PrettyTable, HEADER
        result = ''
        mbeds = self.list_mbeds(unique_names=True, read_details_txt=True)
        if mbeds:
            """ ['platform_name', 'mount_point', 'serial_port', 'target_id'] - columns generated from USB auto-detection
                ['platform_name_unique', ...] - columns generated outside detection subsystem (OS dependent detection)
            """
            columns = ['platform_name', 'platform_name_unique', 'mount_point', 'serial_port', 'target_id', 'daplink_version']
            pt = PrettyTable(columns, junction_char="|", hrules=HEADER)
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

    @deprecated("This method will be removed from the public API. "
                "Please use 'list_mbeds' instead")
    def get_json_data_from_file(self, json_spec_filename, verbose=False):
        """! Loads from file JSON formatted string to data structure
        @return None if JSON can be loaded
        """
        try:
            with open(json_spec_filename) as data_file:
                try:
                    return json.load(data_file)
                except ValueError as json_error_msg:
                    logger.error("Parsing file(%s): %s", json_spec_filename, json_error_msg)
                    return None
        except IOError as fileopen_error_msg:
            logger.warning(fileopen_error_msg)
            return None

    @deprecated("This method will be removed from the public API. "
                "Please use 'list_mbeds' instead")
    def get_htm_target_id(self, mount_point):
        target_id, _ = self._read_htm_ids(mount_point)
        return target_id

    @deprecated("This method will be removed from the public API. "
                "Please use 'list_mbeds' instead")
    def get_mbed_htm(self, mount_point):
        _, build_info = self._read_htm_ids(mount_point)
        return build_info

    @deprecated("This method will be removed from the public API. "
                "Please use 'list_mbeds' instead")
    def get_mbed_htm_comment_section_ver_build(self, line):
        return self._mbed_htm_comment_section_ver_build(line)

    @deprecated("This method will be removed from the public API. "
                "Please use 'list_mbeds' instead")
    def get_mbed_htm_lines(self, mount_point):
        return self._htm_lines(mount_point)

    @deprecated("This method will be removed from the public API. "
                "Please use 'list_mbeds' instead")
    def get_details_txt(self, mount_point):
        return self._details_txt(mount_point)

    @deprecated("This method will be removed from the public API. "
                "Please use 'list_mbeds' instead")
    def parse_details_txt(self, lines):
        return self._parse_details(lines)

    @deprecated("This method will be removed from the public API. "
                "Please use 'list_mbeds' instead")
    def scan_html_line_for_target_id(self, line):
        return self._target_id_from_htm(line)

    @staticmethod
    @deprecated("This method will be removed from the public API. "
                "Please use 'list_mbeds' instead")
    def run_cli_process(cmd, shell=True):
        return MbedLsToolsBase._run_cli_process(cmd, shell)
