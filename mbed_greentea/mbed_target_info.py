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

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""

import re
from mbed_test_api import run_cli_process


TARGET_INFO_MAPPING = {
    "K64F" : {
        "yotta_targets": [
                {
                    "yotta_target": "frdm-k64f-gcc",
                    "mbed_toolchain": "GCC_ARM"
                },
                {
                    "yotta_target": "frdm-k64f-armcc",
                    "mbed_toolchain": "ARM"
                }
             ],
        "properties" : {
                "binary_type": ".bin",
                "copy_method": "default",
                "reset_method": "default",
                "program_cycle_s": 4
            }
    },
    "NUCLEO_F401RE" : {
        "yotta_targets": [
                {
                    "yotta_target": "st-nucleo-f401re-gcc",
                    "mbed_toolchain": "GCC_ARM"
                }
             ],
        "properties" : {
                "binary_type": ".bin",
                "copy_method": "cp",
                "reset_method": "default",
                "program_cycle_s": 4
            }
        }
}

TARGET_TOOLCAHINS = {
    '-armcc': 'ARM',
    '-gcc': 'GCC_ARM',
    '-iar': 'IAR',
}

NOT_SUPPORTED_TESTS = [
    "mbed-test-detect",
    "mbed-test-serial_interrupt",
    "mbed-test-stl",
    "mbed-test-sleep_timeout",
    "mbed-test-blinky",
    "mbed-test-heap_and_stack",
    "mbed-test-cstring",
]

def get_mbed_target_from_current_dir():
    """ Function uses yotta target command to
    """
    result = None
    cmd = ['yotta', 'target']
    print "yotta: search for existing mbed-target"
    _stdout, _stderr, _ret = run_cli_process(cmd)
    if not _ret:
        for line in _stdout.splitlines():
            if ',' in line:
                result = line
                break
    return result

def get_mbed_targets_from_yotta(mbed_classic_name):
    """ Function is using 'yotta search' command to fetch matching mbed device target's name

        Example:
        $ yt search -k mbed-target:k64f target
        frdm-k64f-gcc 0.0.16: Official mbed build target for the mbed frdm-k64f development board.
        frdm-k64f-armcc 0.0.10: Official mbed build target for the mbed frdm-k64f development board, using the armcc toolchain.
    """
    result = []
    cmd = ['yotta', 'search', '-k', 'mbed-target:%s' % mbed_classic_name.lower().strip(), 'target']
    print "yotta: search for mbed-target:%s" % mbed_classic_name.lower().strip()
    _stdout, _stderr, _ret = run_cli_process(cmd)
    if not _ret:
        for line in _stdout.splitlines():
            m = re.search('([\w\d-]+) \d+\.\d+\.\d+:', line)
            if m and len(m.groups()):
                yotta_target_name = m.groups()[0]
                result.append(yotta_target_name)
                print "\tfound target '%s'" % yotta_target_name
    return result

def add_target_info_mapping(mbed_classic_name):
    """ Adds more target information to TARGET_INFO_MAPPING by searching in yotta registry

        Note: function mutates TARGET_INFO_MAPPING
    """
    yotta_target_search = get_mbed_targets_from_yotta(mbed_classic_name)
    # Check if this targets are already there
    if mbed_classic_name not in TARGET_INFO_MAPPING:
        TARGET_INFO_MAPPING[mbed_classic_name] = {
        "yotta_targets": [],
        "properties" : {
                "binary_type": ".bin",
                "copy_method": "default",
                "reset_method": "default",
                "program_cycle_s": 4
            }
        }

    target_desc = TARGET_INFO_MAPPING[mbed_classic_name]
    if 'yotta_targets' in target_desc:
        # All yt targets supported by 'mbed_classic_name' board
        mbeds_yt_targets = []
        for target in target_desc['yotta_targets']:
            mbeds_yt_targets.append(target['yotta_target'])
        # Check if any of yotta targets is new to TARGET_INFO_MAPPING
        for new_yt_target in yotta_target_search:
            if new_yt_target not in mbeds_yt_targets:
                print "\tdiscovered extra target '%s'" % new_yt_target
                # We want to at least guess toolchain type by target's name sufix
                mbed_toolchain = 'UNKNOWN'
                for toolchain_sufix in TARGET_TOOLCAHINS:
                    if new_yt_target.endswith(toolchain_sufix):
                        mbed_toolchain = TARGET_TOOLCAHINS[toolchain_sufix]
                        break

                TARGET_INFO_MAPPING[mbed_classic_name]['yotta_targets'].append({
                    'yotta_target': new_yt_target,
                    'mbed_toolchain': mbed_toolchain
                    })
    return TARGET_INFO_MAPPING

def get_mbed_clasic_target_info(mbed_classic_name):
    """ Function resolves meta-data information about target given as mbed classic name.
        Returns information about yotta target for specific toolchain
    """
    TARGET_INFO_MAPPING = add_target_info_mapping(mbed_classic_name)
    return TARGET_INFO_MAPPING[mbed_classic_name] if mbed_classic_name in TARGET_INFO_MAPPING else None

def get_mbed_supported_test(mbed_test_case_name):
    """ returns true if test case name from mbed SDK can be automated with mbed-greentea
    """
    return mbed_test_case_name not in NOT_SUPPORTED_TESTS
