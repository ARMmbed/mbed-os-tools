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
import os
import json

class MbedLsToolsBase:
    """ Base class for mbed-lstools used by test suite
    """
    def __init__(self):
        """ ctor
        """
        pass

    # Which OSs are supported by this module
    # Note: more than one OS can be supported by mbed-lstools_* module
    os_supported = []

    # Dictionary describing mapping between manufacturers' ids and platform name.
    manufacture_ids = {
        "0700": "NUCLEO_F103RB",
        "0705": "NUCLEO_F302R8",
        "0710": "NUCLEO_L152RE",
        "0715": "NUCLEO_L053R8",
        "0720": "NUCLEO_F401RE",
        "0725": "NUCLEO_F030R8",
        "0730": "NUCLEO_F072RB",
        "0735": "NUCLEO_F334R8",
        "0740": "NUCLEO_F411RE",
        "0745": "NUCLEO_F303RE",

        "1095": "RBLAB_BLENANO",

        "1010": "LPC1768",
        "1040": "LPC11U24",
        "1050": "LPC812",
        "1168": "LPC11U68",
        "1549": "LPC1549",

        "1070": "NRF51822",

        "0231": "KL22Z",
        "0200": "KL25Z",
        "0220": "KL46Z",
        "0230": "K20D50M",
        "0240": "K64F"
    }

    # Interface
    def list_mbeds(self):
        """ Gets information about mbeds connected to device

        MBED_BOARD
        {
            'mount_point' : <>,
            'serial_port' : <>,
            'target_id' : <>,
            'platform_name' : <>,
        }
        # If field unknown, place None

        @return MBED_BOARDS = [ <MBED_BOARD>, ]

        """
        return None

    # Private part, methods used to drive interface functions
    def load_mbed_description(self, file_name):
        """ Loads JSON file with mbeds' description (mapping between target id and platform name)
            Sets self.manufacture_ids with mapping between manufacturers' ids and platform name.
        """
        #self.manufacture_ids = {}   # TODO: load this values from file
        pass

    def err(self, text):
        """ Prints error messages
        """
        print text

    def __str__(self):
        """ Object to string casting
        """
        return self.get_string()

    def get_string(self, border=False, header=True, padding_width=0, sortby='platform_name'):
        """ Printing with some sql table like decorators
        """
        from prettytable import PrettyTable
        from prettytable import PLAIN_COLUMNS
        result = ''
        mbeds = self.list_mbeds()
        if mbeds is not None:
            columns = ['platform_name', 'mount_point', 'serial_port', 'target_id']
            pt = PrettyTable(columns)
            for col in columns:
                pt.align[col] = 'l'

            for mbed in mbeds:
                row = []
                for col in columns:
                    row.append(mbed[col] if col in mbed and mbed[col] is not None else 'unknown')
                pt.add_row(row)
            pt.set_style(PLAIN_COLUMNS)
            result = pt.get_string(border=border, header=header, padding_width=padding_width, sortby=sortby)
        return result

    # Private functions supporting API

    def get_json_data_from_file(self, json_spec_filename, verbose=False):
        """ Loads from file JSON formatted string to data structure
            @return None if JSON can be loaded
        """
        result = None
        try:
            with open(json_spec_filename) as data_file:
                try:
                    result = json.load(data_file)
                except ValueError as json_error_msg:
                    result = None
                    if verbose:
                        print "Error parsing file(%s): %s" % (json_spec_filename, json_error_msg)
        except IOError as fileopen_error_msg:
            if verbose:
                print "Warning: %s" % (fileopen_error_msg)
        return result

    def get_mbed_htm_target_id(self, mount_point):
        """ Function scans mbed.htm to get information about TargetID.
            Function returns targetID, in case of failure returns None.

            Note: This function should be improved to scan variety of boards' mbed.htm files
        """
        result = None
        MBED_HTM_LIST = ['mbed.htm', 'MBED.HTM', 'MBED.htm']
        for mbed_htm in MBED_HTM_LIST:
            mbed_htm_path = os.path.join(mount_point, mbed_htm)
            with open(mbed_htm_path, 'r') as f:
                fline = f.readlines()
                for line in fline:
                    m = re.search('\?code=([a-fA-F0-9]+)', line)
                    if m is not None:
                        result = m.groups()[0]
                        break
        return result
