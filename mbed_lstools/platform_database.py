"""
mbed SDK
Copyright (c) 2017 ARM Limited

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

"""Functions that manage a platform database"""

import datetime
import json
import re
from collections import OrderedDict
from copy import copy
from io import open
from os import makedirs
from os.path import join, dirname, getmtime
from appdirs import user_data_dir
from fasteners import InterProcessLock

try:
    unicode
except NameError:
    unicode = str


import logging
logger = logging.getLogger("mbedls.platform_database")
del logging

LOCAL_PLATFORM_DATABASE = join(user_data_dir("mbedls"), "platforms.json")
LOCAL_MOCKS_DATABASE = join(user_data_dir("mbedls"), "mock.json")

DEFAULT_PLATFORM_DB = {
    u'0001': u'LPC2368',
    u'0002': u'LPC2368',
    u'0003': u'LPC2368',
    u'0004': u'LPC2368',
    u'0005': u'LPC2368',
    u'0006': u'LPC2368',
    u'0007': u'LPC2368',
    u'0100': u'LPC2368',
    u'0183': u'UBLOX_C027',
    u'0200': u'KL25Z',
    u'0201': u'KW41Z',
    u'0210': u'KL05Z',
    u'0214': u'HEXIWEAR',
    u'0217': u'K82F',
    u'0218': u'KL82Z',
    u'0220': u'KL46Z',
    u'0230': u'K20D50M',
    u'0231': u'K22F',
    u'0240': u'K64F',
    u'0245': u'K64F',
    u'0250': u'KW24D',
    u'0261': u'KL27Z',
    u'0262': u'KL43Z',
    u'0300': u'MTS_GAMBIT',
    u'0305': u'MTS_MDOT_F405RG',
    u'0310': u'MTS_DRAGONFLY_F411RE',
    u'0311': u'K66F',
    u'0315': u'MTS_MDOT_F411RE',
    u'0350': u'XDOT_L151CC',
    u'0400': u'MAXWSNENV',
    u'0405': u'MAX32600MBED',
    u'0406': u'MAX32620MBED',
    u'0407': u'MAX32620HSP',
    u'0408': u'MAX32625NEXPAQ',
    u'0409': u'MAX32630FTHR',
    u'0415': u'MAX32625MBED',
    u'0500': u'SPANSION_PLACEHOLDER',
    u'0505': u'SPANSION_PLACEHOLDER',
    u'0510': u'SPANSION_PLACEHOLDER',
    u'0602': u'EV_COG_AD3029LZ',
    u'0603': u'EV_COG_AD4050LZ',
    u'0700': u'NUCLEO_F103RB',
    u'0705': u'NUCLEO_F302R8',
    u'0710': u'NUCLEO_L152RE',
    u'0715': u'NUCLEO_L053R8',
    u'0720': u'NUCLEO_F401RE',
    u'0725': u'NUCLEO_F030R8',
    u'0730': u'NUCLEO_F072RB',
    u'0735': u'NUCLEO_F334R8',
    u'0740': u'NUCLEO_F411RE',
    u'0743': u'DISCO_F413ZH',
    u'0744': u'NUCLEO_F410RB',
    u'0745': u'NUCLEO_F303RE',
    u'0747': u'NUCLEO_F303ZE',
    u'0750': u'NUCLEO_F091RC',
    u'0755': u'NUCLEO_F070RB',
    u'0760': u'NUCLEO_L073RZ',
    u'0764': u'DISCO_L475VG_IOT01A',
    u'0765': u'NUCLEO_L476RG',
    u'0766': u'SILICA_SENSOR_NODE',
    u'0770': u'NUCLEO_L432KC',
    u'0775': u'NUCLEO_F303K8',
    u'0777': u'NUCLEO_F446RE',
    u'0778': u'NUCLEO_F446ZE',
    u'0779': u'NUCLEO_L433RC_P',
    u'0780': u'NUCLEO_L011K4',
    u'0785': u'NUCLEO_F042K6',
    u'0788': u'DISCO_F469NI',
    u'0790': u'NUCLEO_L031K6',
    u'0791': u'NUCLEO_F031K6',
    u'0795': u'DISCO_F429ZI',
    u'0796': u'NUCLEO_F429ZI',
    u'0797': u'NUCLEO_F439ZI',
    u'0799': u'ST_PLACEHOLDER',
    u'0805': u'DISCO_L053C8',
    u'0810': u'DISCO_F334C8',
    u'0812': u'NUCLEO_F722ZE',
    u'0813': u'NUCLEO_H743ZI',
    u'0815': u'DISCO_F746NG',
    u'0816': u'NUCLEO_F746ZG',
    u'0817': u'DISCO_F769NI',
    u'0818': u'NUCLEO_F767ZI',
    u'0819': u'NUCLEO_F756ZG',
    u'0820': u'DISCO_L476VG',
    u'0821': u'NUCLEO_L452RE',
    u'0823': u'NUCLEO_L496ZG',
    u'0824': u'LPC824',
    u'0826': u'NUCLEO_F412ZG',
    u'0827': u'NUCLEO_L486RG',
    u'0828': u'NUCLEO_L496ZG_P',
    u'0829': u'NUCLEO_L452RE_P',
    u'0830': u'DISCO_F407VG',
    u'0833': u'DISCO_L072CZ_LRWAN1',
    u'0835': u'NUCLEO_F207ZG',
    u'0840': u'B96B_F446VE',
    u'0900': u'XPRO_SAMR21',
    u'0905': u'XPRO_SAMW25',
    u'0910': u'XPRO_SAML21',
    u'0915': u'XPRO_SAMD21',
    u'1000': u'LPC2368',
    u'1001': u'LPC2368',
    u'1010': u'LPC1768',
    u'1017': u'HRM1017',
    u'1018': u'SSCI824',
    u'1019': u'TY51822R3',
    u'1022': u'RO359B',
    u'1034': u'LPC11U34',
    u'1040': u'LPC11U24',
    u'1045': u'LPC11U24',
    u'1050': u'LPC812',
    u'1054': u'LPC54114',
    u'1056': u'LPC546XX',
    u'1060': u'LPC4088',
    u'1061': u'LPC11U35_401',
    u'1062': u'LPC4088_DM',
    u'1070': u'NRF51822',
    u'1075': u'NRF51822_OTA',
    u'1080': u'OC_MBUINO',
    u'1090': u'RBLAB_NRF51822',
    u'1095': u'RBLAB_BLENANO',
    u'1100': u'NRF51_DK',
    u'1101': u'NRF52_DK',
    u'1102': u'NRF52840_DK',
    u'1105': u'NRF51_DK_OTA',
    u'1114': u'LPC1114',
    u'1120': u'NRF51_DONGLE',
    u'1130': u'NRF51822_SBK',
    u'1140': u'WALLBOT_BLE',
    u'1168': u'LPC11U68',
    u'1200': u'NCS36510',
    u'1234': u'UBLOX_C027',
    u'1235': u'UBLOX_C027',
    u'1236': u'UBLOX_EVK_ODIN_W2',
    u'1237': u'UBLOX_EVK_NINA_B1',
    u'1300': u'NUC472-NUTINY',
    u'1301': u'NUMBED',
    u'1302': u'NUMAKER_PFM_NUC472',
    u'1303': u'NUMAKER_PFM_M453',
    u'1304': u'NUMAKER_PFM_M487',
    u'1305': u'NUMAKER_PFM_M2351',
    u'1306': u'NUMAKER_PFM_NANO130',
    u'1307': u'NUMAKER_PFM_NUC240',
    u'1549': u'LPC1549',
    u'1600': u'LPC4330_M4',
    u'1605': u'LPC4330_M4',
    u'2000': u'EFM32_G8XX_STK',
    u'2005': u'EFM32HG_STK3400',
    u'2010': u'EFM32WG_STK3800',
    u'2015': u'EFM32GG_STK3700',
    u'2020': u'EFM32LG_STK3600',
    u'2025': u'EFM32TG_STK3300',
    u'2030': u'EFM32ZG_STK3200',
    u'2035': u'EFM32PG_STK3401',
    u'2040': u'EFM32PG12_STK3402',
    u'2041': u'TB_SENSE_12',
    u'2045': u'TB_SENSE_1',
    u'2100': u'XBED_LPC1768',
    u'2201': u'WIZWIKI_W7500',
    u'2202': u'WIZWIKI_W7500ECO',
    u'2203': u'WIZWIKI_W7500P',
    u'2500': u'ADV_WISE_1570',
    u'3001': u'LPC11U24',
    u'4000': u'LPC11U35_Y5_MBUG',
    u'4005': u'NRF51822_Y5_MBUG',
    u'4100': u'MOTE_L152RC',
    u'4337': u'LPC4337',
    u'4500': u'DELTA_DFCM_NNN40',
    u'4501': u'DELTA_DFBM_NQ620',
    u'4502': u'DELTA_DFCM_NNN50',
    u'4600': u'REALTEK_RTL8195AM',
    u'5000': u'ARM_MPS2',
    u'5001': u'ARM_MPS2_M0',
    u'5002': u'ARM_BEETLE_SOC',
    u'5003': u'ARM_MPS2_M0P',
    u'5005': u'ARM_MPS2_M0DS',
    u'5007': u'ARM_MPS2_M1',
    u'5009': u'ARM_MPS2_M3',
    u'5011': u'ARM_MPS2_M4',
    u'5015': u'ARM_MPS2_M7',
    u'5020': u'HOME_GATEWAY_6LOWPAN',
    u'5500': u'RZ_A1H',
    u'5501': u'GR_LYCHEE',
    u'6660': u'NZ32_SC151',
    u'7010': u'BLUENINJA_CDP_TZ01B',
    u'7011': u'TMPM066',
    u'7013': u'TMPM46B',
    u'7402': u'MBED_BR_HAT',
    u'7778': u'TEENSY3_1',
    u'8001': u'UNO_91H',
    u'9001': u'LPC1347',
    u'9002': u'LPC11U24',
    u'9003': u'LPC1347',
    u'9004': u'ARCH_PRO',
    u'9006': u'LPC11U24',
    u'9007': u'LPC11U35_501',
    u'9008': u'XADOW_M0',
    u'9009': u'ARCH_BLE',
    u'9010': u'ARCH_GPRS',
    u'9011': u'ARCH_MAX',
    u'9012': u'SEEED_TINY_BLE',
    u'9900': u'NRF51_MICROBIT',
    u'C002': u'VK_RZ_A1H',
    u'C005': u'MTM_MTCONNECT04S',
    u'C006': u'VBLUNO51',
    u'C030': u'UBLOX_C030_U201',
    u'C031': u'UBLOX_C030_N211',
    u'C032': u'UBLOX_C030_R404M',
    u'C033': u'UBLOX_C030_R410M',
    u'C034': u'UBLOX_C030_S200',
    u'C035': u'UBLOX_C030_R3121',
    u'FFFF': u'K20 BOOTLOADER',
    u'RIOT': u'RIOT',
}


def _get_modified_time(path):
    try:
        mtime = getmtime(path)
    except OSError:
        mtime = 0
    return datetime.date.fromtimestamp(mtime)


def _older_than_me(path):
    return _get_modified_time(path) < _get_modified_time(__file__)


def _overwrite_or_open(db):
    try:
        if db is LOCAL_PLATFORM_DATABASE and _older_than_me(db):
            raise ValueError("Platform Database is out of date")
        with open(db, encoding="utf-8") as db_in:
            return json.load(db_in)
    except (IOError, ValueError) as exc:
        if db is LOCAL_PLATFORM_DATABASE:
            logger.warning(
                "Error loading database %s: %s; Recreating", db, str(exc))
            try:
                makedirs(dirname(db))
            except OSError:
                pass
            with open(db, "w", encoding="utf-8") as out:
                out.write(unicode(json.dumps(DEFAULT_PLATFORM_DB)))
            return copy(DEFAULT_PLATFORM_DB)
        else:
            return {}


class PlatformDatabase(object):
    """Represents a union of multiple platform database files.
    Handles inter-process synchronization of database files.
    """

    target_id_pattern = re.compile(r'^[a-fA-F0-9]{4}$')

    def __init__(self, database_files, primary_database=None):
        """Construct a PlatformDatabase object from a series of platform database files"""
        self._prim_db = primary_database
        if not self._prim_db and len(database_files) == 1:
            self._prim_db = database_files[0]
        self._dbs = OrderedDict()
        self._keys = set()
        for db in database_files:
            new_db = _overwrite_or_open(db)
            duplicates = set(self._keys).intersection(set(new_db.keys()))
            if duplicates:
                logger.warning(
                    "Duplicate platform ids found: %s,"
                    " ignoring the definitions from %s",
                    " ".join(duplicates), db)
            self._dbs[db] = new_db
            self._keys = self._keys.union(new_db.keys())

    def items(self):
        for db in self._dbs.values():
            for entry in db.items():
                yield entry

    def all_ids(self):
        return iter(self._keys)

    def get(self, index, default=None):
        """Standard lookup function. Works exactly like a dict"""
        for db in self._dbs.values():
            maybe_answer = db.get(index, None)
            if maybe_answer:
                return maybe_answer

        return default

    def _update_db(self):
        if self._prim_db:
            lock = InterProcessLock("%s.lock" % self._prim_db)
            acquired = lock.acquire(blocking=False)
            if not acquired:
                logger.debug("Waiting 60 seconds for file lock")
                acquired = lock.acquire(blocking=True, timeout=60)
            if acquired:
                try:
                    with open(self._prim_db, "w", encoding="utf-8") as out:
                        out.write(unicode(
                            json.dumps(self._dbs[self._prim_db])))
                    return True
                finally:
                    lock.release()
            else:
                logger.error("Could not update platform database: "
                             "Lock acquire failed after 60 seconds")
                return False
        else:
            logger.error("Can't update platform database: "
                         "destination database is ambiguous")
            return False

    def add(self, id, platform_name, permanent=False):
        """Add a platform to this database, optionally updating an origin
        database
        """
        if self.target_id_pattern.match(id):
            if self._prim_db:
                self._dbs[self._prim_db][id] = platform_name
            else:
                next(iter(self._dbs.values()))[id] = platform_name
            self._keys.add(id)
            if permanent:
                self._update_db()
        else:
            raise ValueError("Invald target id: %s" % id)

    def remove(self, id, permanent=False):
        """Remove a platform from this database, optionally updating an origin
        database
        """
        logger.debug("Trying remove of %s", id)
        if id is '*':
            self._dbs[self._prim_db] = {}
        for db in self._dbs.values():
            if id in db:
                logger.debug("Removing id...")
                removed = db[id]
                del db[id]
                self._keys.remove(id)
                if permanent:
                    self._update_db()
                return removed
