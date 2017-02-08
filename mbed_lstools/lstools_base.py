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
from fasteners import InterProcessLock


def timed_mbedls_lock(timeout):
    """
    Implements Inter Process Lock using fasteners.InterProcessLock and adding a timeout feature to avoid wait forever.

    :param timeout:     Time to wait for acquiring lock. Else an exception is raised.
    :return:
    """
    def wrapper(self, *args):
        ret = None
        lock = InterProcessLock(self.lock_file)
        acquired = lock.acquire(blocking=False)
        if not acquired:
            self.debug("timed_mbedls_lock", "Waiting %d seconds for mock file lock." % timeout)
            acquired = lock.acquire(blocking=True, timeout=timeout)
        if acquired:
            try:
                ret = wrapper.original(self, *args)
            except Exception as e:
                lock.release()
                raise e
            lock.release()
        else:
            self.err("timed_mbedls_lock", "Failed to acquired mock file lock in %d seconds!" % timeout)
            sys.exit(1)
        return ret

    def func(original):
        wrapper.original = original
        return wrapper
    return func


class MbedLsToolsBase:
    """ Base class for mbed-lstools, defines mbed-ls tools interface for mbed-enabled devices detection for various hosts
    """
    def __init__(self, **kwargs):
        """ ctor
        """
        #extra flags
        self.DEBUG_FLAG = False     # Used to enable debug code / prints
        self.ERRORLEVEL_FLAG = 0    # Used to return success code to environment
        self.retarget_data = {}          # Used to retarget mbed-enabled platform properties

        # Create in HOME directory place for mbed-ls to store information
        self.mbedls_home_dir_init()
        self.lock_file = os.path.join(MbedLsToolsBase.HOME_DIR,
                                      MbedLsToolsBase.MBEDLS_HOME_DIR, MbedLsToolsBase.MBEDLS_GLOBAL_LOCK)
        self.mbedls_get_mocks()
        # skip retarget if specified to skip in arguments
        if 'skip_retarget' not in kwargs or not kwargs['skip_retarget']:
            self.retarget()

    # Which OSs are supported by this module
    # Note: more than one OS can be supported by mbed-lstools_* module
    os_supported = []

    # Dictionary describing mapping between manufacturers' ids and platform name.
    manufacture_ids = {
        "0001": "LPC2368",
        "0002": "LPC2368",
        "0003": "LPC2368",
        "0004": "LPC2368",
        "0005": "LPC2368",
        "0006": "LPC2368",
        "0007": "LPC2368",
        "0100": "LPC2368",
        "0183": "UBLOX_C027",
        "0200": "KL25Z",
        "0201": "KW41Z",
        "0210": "KL05Z",
        "0214": "HEXIWEAR",
        "0217": "K82F",
        "0218": "KL82Z",
        "0220": "KL46Z",
        "0230": "K20D50M",
        "0231": "K22F",
        "0240": "K64F",
        "0245": "K64F",
        "0250": "KW24D",
        "0261": "KL27Z",
        "0262": "KL43Z",
        "0300": "MTS_GAMBIT",
        "0305": "MTS_MDOT_F405RG",
        "0310": "MTS_DRAGONFLY_F411RE",
        "0311": "K66F",
        "0315": "MTS_MDOT_F411RE",
        "0350": "XDOT_L151CC",
        "0400": "MAXWSNENV",
        "0405": "MAX32600MBED",
        "0406": "MAX32620MBED",
        "0407": "MAX32620HSP",
        "0408": "MAX32625NEXPAQ",
        "0409": "MAX32630FTHR",
        "0415": "MAX32625MBED",
        "0500": "SPANSION_PLACEHOLDER",
        "0505": "SPANSION_PLACEHOLDER",
        "0510": "SPANSION_PLACEHOLDER",
        "0700": "NUCLEO_F103RB",
        "0705": "NUCLEO_F302R8",
        "0710": "NUCLEO_L152RE",
        "0715": "NUCLEO_L053R8",
        "0720": "NUCLEO_F401RE",
        "0725": "NUCLEO_F030R8",
        "0730": "NUCLEO_F072RB",
        "0735": "NUCLEO_F334R8",
        "0740": "NUCLEO_F411RE",
        "0744": "NUCLEO_F410RB",
        "0745": "NUCLEO_F303RE",
        "0747": "NUCLEO_F303ZE",
        "0750": "NUCLEO_F091RC",
        "0755": "NUCLEO_F070RB",
        "0760": "NUCLEO_L073RZ",
        "0765": "NUCLEO_L476RG",
        "0770": "NUCLEO_L432KC",
        "0775": "NUCLEO_F303K8",
        "0777": "NUCLEO_F446RE",
        "0778": "NUCLEO_F446ZE",
        "0780": "NUCLEO_L011K4",
        "0785": "NUCLEO_F042K6",
        "0788": "DISCO_F469NI",
        "0790": "NUCLEO_L031K6",
        "0791": "NUCLEO_F031K6",
        "0795": "DISCO_F429ZI",
        "0796": "NUCLEO_F429ZI",
        "0797": "NUCLEO_F439ZI",
        "0799": "ST_PLACEHOLDER",
        "0805": "DISCO_L053C8",
        "0810": "DISCO_F334C8",
        "0815": "DISCO_F746NG",
        "0816": "NUCLEO_F746ZG",
        "0817": "DISCO_F769NI",
        "0818": "NUCLEO_F767ZI",
        "0819": "NUCLEO_F756ZG",
        "0820": "DISCO_L476VG",
        "0824": "LPC824",
        "0826": "NUCLEO_F412ZG",
        "0827": "NUCLEO_L486RG",
        "0835": "NUCLEO_F207ZG",
        "0840": "B96B_F446VE",
        "0900": "XPRO_SAMR21",
        "0905": "XPRO_SAMW25",
        "0910": "XPRO_SAML21",
        "0915": "XPRO_SAMD21",
        "1000": "LPC2368",
        "1001": "LPC2368",
        "1010": "LPC1768",
        "1017": "HRM1017",
        "1018": "SSCI824",
        "1019": "TY51822R3",
        "1022": "BP359B",
        "1034": "LPC11U34",
        "1040": "LPC11U24",
        "1045": "LPC11U24",
        "1050": "LPC812",
        "1060": "LPC4088",
        "1061": "LPC11U35_401",
        "1062": "LPC4088_DM",
        "1070": "NRF51822",
        "1075": "NRF51822_OTA",
        "1080": "OC_MBUINO",
        "1090": "RBLAB_NRF51822",
        "1095": "RBLAB_BLENANO",
        "1100": "NRF51_DK",
        "1101": "NRF52_DK",
        "1105": "NRF51_DK_OTA",
        "1114": "LPC1114",
        "1120": "NRF51_DONGLE",
        "1130": "NRF51822_SBK",
        "1140": "WALLBOT_BLE",
        "1168": "LPC11U68",
        "1200": "NCS36510",
        "1234": "UBLOX_C027",
        "1235": "UBLOX_C027",
        "1236": "UBLOX_EVK_ODIN_W2",
        "1300": "NUC472-NUTINY",
        "1301": "NUMBED",
        "1302": "NUMAKER_PFM_NUC472",
        "1303": "NUMAKER_PFM_M453",
        "1304": "NUMAKER_PFM_M487",
        "1549": "LPC1549",
        "1600": "LPC4330_M4",
        "1605": "LPC4330_M4",
        "2000": "EFM32_G8XX_STK",
        "2005": "EFM32HG_STK3400",
        "2010": "EFM32WG_STK3800",
        "2015": "EFM32GG_STK3700",
        "2020": "EFM32LG_STK3600",
        "2025": "EFM32TG_STK3300",
        "2030": "EFM32ZG_STK3200",
        "2035": "EFM32PG_STK3401",
        "2100": "XBED_LPC1768",
        "2201": "WIZWIKI_W7500",
        "2202": "WIZWIKI_W7500ECO",
        "2203": "WIZWIKI_W7500P",
        "3001": "LPC11U24",
        "4000": "LPC11U35_Y5_MBUG",
        "4005": "NRF51822_Y5_MBUG",
        "4100": "MOTE_L152RC",
        "4337": "LPC4337",
        "4500": "DELTA_DFCM_NNN40",
        "4501": "DELTA_DFBM_NQ620",
        "4502": "DELTA_DFCM_NNN50",
        "4600": "REALTEK_RTL8195AM",
        "5000": "ARM_MPS2",
        "5001": "ARM_MPS2_M0",
        "5003": "ARM_BEETLE_SOC",
        "5005": "ARM_MPS2_M0DS",
        "5007": "ARM_MPS2_M1",
        "5009": "ARM_MPS2_M3",
        "5011": "ARM_MPS2_M4",
        "5015": "ARM_MPS2_M7",
        "5020": "HOME_GATEWAY_6LOWPAN",
        "5500": "RZ_A1H",
        "5501": "RZ_A1LU"
        "6660": "NZ32_SC151",
        "7010": "BLUENINJA_CDP_TZ01B",
        "7011": "TMPM066",
        "7778": "TEENSY3_1",
        "8001": "UNO_91H",
        "9001": "LPC1347",
        "9002": "LPC11U24",
        "9003": "LPC1347",
        "9004": "ARCH_PRO",
        "9006": "LPC11U24",
        "9007": "LPC11U35_501",
        "9008": "XADOW_M0",
        "9009": "ARCH_BLE",
        "9010": "ARCH_GPRS",
        "9011": "ARCH_MAX",
        "9012": "SEEED_TINY_BLE",
        "9900": "NRF51_MICROBIT",
        "C002": "VK_RZ_A1H",
        "FFFF": "K20 BOOTLOADER",
        "RIOT": "RIOT",
    }

    # Directory where we will store global (OS user specific mocking)
    HOME_DIR = expanduser("~")
    MBEDLS_HOME_DIR = '.mbed-ls'
    MOCK_FILE_NAME = '.mbedls-mock'
    MBEDLS_GLOBAL_LOCK = 'mbedls-lock'
    MOCK_HOME_FILE_NAME = os.path.join(HOME_DIR, MBEDLS_HOME_DIR, MOCK_FILE_NAME)
    RETARGET_FILE_NAME = 'mbedls.json'
    DETAILS_TXT_NAME = 'DETAILS.TXT'
    MBED_HTM_NAME = 'mbed.htm'

    def mbedls_home_dir_init(self):
        """! Initialize data in home directory for locking features
        @details Create '.mbed-ls' sub-directory in current user $HOME directory
        """
        if not os.path.isdir(os.path.join(self.HOME_DIR, self.MBEDLS_HOME_DIR)):
            try:
                os.makedirs(os.path.join(self.HOME_DIR, self.MBEDLS_HOME_DIR))
            except os.error as e:
                self.err(str(e))

    def mbedls_get_mocks(self):
        """! Load existing mocking configuration from current user $HOME directory
        @details If there is a local mocking data use it and add / override manufacture_ids
        """
        mock_ids = self.mock_read()
        if mock_ids:
            self.debug(self.mbedls_get_mocks.__name__, "mock data found, %d entries"% len(mock_ids))
            for mid in mock_ids:
                self.manufacture_ids[mid] = mock_ids[mid]

    def list_manufacture_ids(self):
        """! Creates list of all available mappings for target_id -> Platform
        @return String with table formatted output
        """
        from prettytable import PrettyTable

        columns = ['target_id_prefix', 'platform_name']
        pt = PrettyTable(columns)
        for col in columns:
            pt.align[col] = 'l'

        for target_id_prefix in sorted(self.manufacture_ids.keys()):
            platform_name = self.manufacture_ids[target_id_prefix]
            pt.add_row([target_id_prefix, platform_name])

        return pt.get_string()

    @timed_mbedls_lock(60)
    def mock_read(self):
        """! Load mocking data from local file
        @details Uses file locking for operation on Mock
                 configuration file in current user $HOME directory
        @return Curent mocking configuration (dictionary)
        """
        def read_mock_file(filename):
            try:
                with open(filename, "r") as f:
                    return json.load(f)
            except IOError as e:
                self.err("reading file '%s' failed: %s"% (os.path.abspath(filename),
                    str(e)))
            except ValueError as e:
                self.err("reading file '%s' content failed: %s"% (os.path.abspath(filename),
                    str(e)))
            return {}

        result = {}

        # This read is for backward compatibility
        # When user already have on its system local mock-up it will work
        # overwriting global one
        if isfile(self.MOCK_FILE_NAME):
            result = read_mock_file(self.MOCK_FILE_NAME)
        elif isfile(self.MOCK_HOME_FILE_NAME):
            result = read_mock_file(self.MOCK_HOME_FILE_NAME)

        return result

    @timed_mbedls_lock(60)
    def mock_write(self, mock_ids):
        """! Write current mocking structure
        @param mock_ids JSON mock data to dump to file
        @details Uses file locking for operation on Mock
                 configuration file in current user $HOME directory
        @return True if configuration operation was success, else False
        """
        def write_mock_file(filename, mock_ids):
            try:
                with open(filename, "w") as f:
                    f.write(json.dumps(mock_ids, indent=4))
                    return True
            except IOError as e:
                self.err("writing file '%s' failed: %s"% (os.path.abspath(filename),
                    str(e)))
            except ValueError as e:
                self.err("writing file '%s' content failed: %s"% (os.path.abspath(filename),
                    str(e)))
            return False

        result = write_mock_file(self.MOCK_HOME_FILE_NAME, mock_ids)

        return result

    def retarget_read(self):
        """! Load retarget data from local file
        @return Curent retarget configuration (dictionary)
        """
        if os.path.isfile(self.RETARGET_FILE_NAME):
            self.debug(self.retarget_read.__name__, "reading retarget file %s"% self.RETARGET_FILE_NAME)
            try:
                with open(self.RETARGET_FILE_NAME, "r") as f:
                    return json.load(f)
            except IOError as e:
                self.err("reading file '%s' failed: %s"% (os.path.abspath(self.RETARGET_FILE_NAME),
                    str(e)))
            except ValueError as e:
                self.err("reading file '%s' content failed: %s"% (os.path.abspath(self.RETARGET_FILE_NAME),
                    str(e)))
        return {}

    def retarget(self):
        """! Enable retargeting
        @details Read data from local retarget configuration file
        @return Retarget data structure read from configuration file
        """
        self.retarget_data = self.retarget_read()
        return self.retarget_data

    def mock_manufacture_ids(self, mid, platform_name, oper='+'):
        """! Replace (or add if manufacture id doesn't exist) entry in self.manufacture_ids
        @param oper '+' add new mock / override existing entry
                    '-' remove mid from mocking entry
        @return Mocked structure (json format)
        """
        mock_ids = self.mock_read()

        # Operations on mocked structure
        if oper == '+':
            mock_ids[mid] = platform_name
            self.debug(self.mock_manufacture_ids.__name__, "mock_ids['%s'] = '%s'"% (mid, platform_name))
        elif oper in ['-', '!']:
            if mid in mock_ids:
                mock_ids.pop(mid)
                self.debug(self.mock_manufacture_ids.__name__, "removing '%s' mock"% mid)
            elif mid == '*':
                mock_ids = {}   # Zero mocking set
                self.debug(self.mock_manufacture_ids.__name__, "zero mocking set")

        self.mock_write(mock_ids)
        return mock_ids

    # Note: 'Ven_SEGGER' - This is used to detect devices from EFM family, they use Segger J-LInk to wrap MSD and CDC
    usb_vendor_list = ['Ven_MBED', 'Ven_SEGGER']

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
                    self.debug(self.list_mbeds_ext.__name__, ("retargeting", target_id, mbeds[i]))

            # Add interface chip meta data to mbed structure
            details_txt = self.get_details_txt(val['mount_point'])
            if details_txt:
                for field in details_txt:
                    field_name = 'daplink_' + field.lower().replace(' ', '_')
                    if field_name not in mbeds[i]:
                        mbeds[i][field_name] = details_txt[field]

            mbed_htm = self.get_mbed_htm(val['mount_point'])
            if mbed_htm:
                for field in mbed_htm:
                    field_name = 'daplink_' + field.lower().replace(' ', '_')
                    if field_name not in mbeds[i]:
                        mbeds[i][field_name] = mbed_htm[field]

            self.debug(self.list_mbeds_ext.__name__, (mbeds[i]['platform_name_unique'], val['target_id']))
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

    # Private part, methods used to drive interface functions
    def load_mbed_description(self, file_name):
        """! Load JSON file with mbeds' description (mapping between target id and platform name)
            Sets self.manufacture_ids with mapping between manufacturers' ids and platform name.
        """
        #self.manufacture_ids = {}   # TODO: load this values from file
        pass

    def err(self, text):
        """! Prints error messages
        @param text Text to be included in error message
        @details Function prints directly on console
        """
        print('error: {}'.format(text))

    def debug(self, name, text):
        """! Prints error messages
        @param name Called function name
        @param text Text to be included in debug message
        @details Function prints directly on console
        """
        if self.DEBUG_FLAG:
            print('debug @%s.%s: %s'% (self.__class__.__name__, name, text))

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
                    if verbose:
                        print("Error parsing file(%s): %s" % (json_spec_filename, json_error_msg))
        except IOError as fileopen_error_msg:
            if verbose:
                print("Warning: %s" % (fileopen_error_msg))
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
                            self.debug(self.get_mbed_htm_target_id.__name__, ('Failed to open file', mbed_htm_path))
            except OSError:
                self.debug(self.get_mbed_htm_target_id.__name__, ('Failed to list mount point', mount_point))

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
                    self.debug(self.get_details_txt.__name__, ('Failed to open file', path_to_details_txt + '\n' + str(e)))
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
            self.debug(self.scan_html_line_for_target_id.__name__, line.strip())
            self.debug(self.scan_html_line_for_target_id.__name__, (m.groups(), result))
            return result
        # Last resort, we can try to see if old mbed.htm format is there
        else:
            m = re.search('\?auth=([a-fA-F0-9]+)', line)
            if m:
                result = m.groups()[0]
                self.debug(self.scan_html_line_for_target_id.__name__, line.strip())
                self.debug(self.scan_html_line_for_target_id.__name__, (m.groups(), result))
                return result
        return None

    def mount_point_ready(self, path):
        """! Check if a mount point is ready for file operations
        @return Returns True if the given path exists, False otherwise
        """
        result = os.path.exists(path)

        if result:
            self.debug(self.mount_point_ready.__name__, "Mount point %s is ready" % path)
        else:
            self.debug(self.mount_point_ready.__name__, "Mount point %s does not exist" % (path))

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
