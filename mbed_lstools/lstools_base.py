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
        "0183": "ARM-MBED-BASED-STARTER-KIT-FOR-IBM-IOT-CLOUD",
        "0200": "KL25Z",
        "0210": "FRDM-KL05Z",
        "0220": "FRDM-KL46Z",
        "0230": "FRDM-K20D50M",
        "0231": "FRDM-K22F",
        "0240": "FRDM-K64F",
        "0245": "IBMETHERNETKIT",
        "0300": "MTS-GAMBIT",
        "0305": "MTS-MDOT-F405",
        "0310": "MTS-DRAGONFLY",
        "0315": "MTS-MDOT-F411",
        "0400": "MAXWSNENV",
        "0405": "MAX32600MBED",
        "0500": "FM0P",
        "0505": "FM3",
        "0510": "FM4",
        "0700": "ST-NUCLEO-F103RB",
        "0705": "ST-NUCLEO-F302R8",
        "0710": "ST-NUCLEO-L152RE",
        "0715": "ST-NUCLEO-L053R8",
        "0720": "ST-NUCLEO-F401RE",
        "0725": "ST-NUCLEO-F030R8",
        "0730": "ST-NUCLEO-F072RB",
        "0735": "ST-NUCLEO-F334R8",
        "0740": "ST-NUCLEO-F411RE",
        "0745": "ST-NUCLEO-F303RE",
        "0750": "ST-NUCLEO-F091RC",
        "0755": "ST-NUCLEO-F070RB",
        "0760": "ST-NUCLEO-L073RZ",
        "0765": "ST-NUCLEO-RESERVED",
        "0770": "ST-NUCLEO-L433KC",
        "0775": "ST-NUCLEO-F303K8",
        "0780": "ST-NUCLEO-F031K6",
        "0785": "ST-NUCLEO-F042K6",
        "0790": "ST-NUCLEO-L031K6",
        "0795": "ST-NUCLEO-L021K6",
        "0799": "ST-PLATFORMS",
        "0805": "ST-DISCOVERY-L053C8",
        "0810": "ST-DISCOVERY-F334C8",
        "0815": "ST-DISCOVERY-F746NG",
        "0820": "ST-DISCOVERY-L476VG",
        "0824": "LPCXPRESSO824-MAX",
        "1000": "MBED-LPC2368",
        "1010": "MBED-LPC1768",
        "1017": "MBED-HRM1017",
        "1018": "SWITCH-SCIENCE-MBED-LPC824",
        "1030": "CSR-BLACKADDER",
        "1034": "MICRONFCBOARD",
        "1040": "MBED-LPC11U24",
        "1045": "ROBOTIKY",
        "1050": "NXP-LPC800-MAX",
        "1060": "EA-LPC4088",
        "1061": "EA-LPC11U35",
        "1062": "EA-LPC4088-DISPLAY-MODULE",
        "1070": "NORDIC-NRF51822",
        "1075": "NORDIC-NRF51822-FOTA",
        "1080": "OUTRAGEOUS-CIRCUITS-MBUINO",
        "1090": "REDBEARLAB-NRF51822",
        "1095": "REDBEARLAB-BLE-NANO",
        "1100": "NORDIC-NRF51-DK",
        "1105": "NORDIC-NRF51-DK-FOTA",
        "1114": "LPC1114FN28",
        "1120": "NORDIC-NRF51-DONGLE",
        "1130": "NORDIC-SMART-BEACON-KIT",
        "1140": "JKSOFT-WALLBOT-BLE",
        "1168": "LPCXPRESSO11U68",
        "1234": "U-BLOX-C027",
        "1235": "U-BLOX-C027-NATIVE",
        "1549": "LPCXPRESSO1549",
        "1600": "MICROMINT-BAMBINO-210",
        "1605": "MICROMINT-BAMBINO-210E",
        "2000": "EFM32-GECKO",
        "2005": "EFM32-HAPPY-GECKO",
        "2010": "EFM32-WONDER-GECKO",
        "2015": "EFM32-GIANT-GECKO",
        "2020": "EFM32-LEOPARD-GECKO",
        "2025": "EFM32-TINY-GECKO",
        "2030": "EFM32-ZERO-GECKO",
        "2100": "XBED-LPC1768",
        "3001": "RENBED-LPC11U24",
        "4000": "Y5-LPC11U35-MBUG",
        "4005": "Y5-NRF51822-MBUG",
        "4100": "NAMOTE-72",
        "4337": "LPCXPRESSO4337",
        "4500": "DELTA-DFCM-NNN40",
        "5000": "ARM-MPS2",
        "5001": "ARM-MPS2-M0",
        "5003": "ARM-MPS2-M0P",
        "5005": "ARM-MPS2-M0DS",
        "5007": "ARM-MPS2-M1",
        "5009": "ARM-MPS2-M3",
        "5011": "ARM-MPS2-M4",
        "5015": "ARM-MPS2-M7",
        "5020": "HOME-GATEWAY-6LOWPAN",
        "5500": "RENESAS-GR-PEACH",
        "7777": "MBED-LPC1768-EXP",
        "7778": "TEENSY-3-1",
        "9001": "DIPCORTEX-M3",
        "9002": "BLUEBOARD-LPC11U24",
        "9003": "WIFI-DIPCORTEX",
        "9004": "SEEEDUINO-ARCH-PRO",
        "9006": "SEEEDUINO-ARCH",
        "9007": "TG-LPC11U35-501",
        "9008": "SEEED-XADOW-M0",
        "9009": "SEEED-ARCH-BLE",
        "9010": "SEEED-ARCH-GPRS",
        "9011": "SEEED-ARCH-MAX",
        "9012": "SEEED-TINY-BLE",
        "9990": "CORTEX-M4F-UARM",
        "9991": "CORTEX-M4F-ARM",
        "9992": "CORTEX-M4-UARM",
        "9993": "CORTEX-M4-ARM",
        "9994": "CORTEX-M3-UARM",
        "9995": "CORTEX-M3-ARM",
        "9996": "CORTEX-M0P-UARM",
        "9997": "CORTEX-M0P-ARM",
        "9998": "CORTEX-M0-UARM",
        "9999": "CORTEX-M0-ARM",
        "FFFF": "MBED-K20DX128-BOOTLOADER",
        "RIOT": "RIOT",
    }

    #
    # Note: 'Ven_SEGGER' - This is used to detect devices from EFM family, they use Segger J-LInk to wrap MSD and CDC
    usb_vendor_list = ['Ven_MBED', 'Ven_SEGGER']

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
                    # Detecting modern mbed.htm file format
                    m = re.search('\?code=([a-fA-F0-9]+)', line)
                    if m is not None:
                        result = m.groups()[0]
                        break
                    # Last resort, we can try to see if old mbed.htm format is there
                    else:
                        m = re.search('\?auth=([a-fA-F0-9]+)', line)
                        if m is not None:
                            result = m.groups()[0]
                            break
        return result
