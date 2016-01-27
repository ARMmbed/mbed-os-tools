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

import os
import re
import json
from mbed_test_api import run_cli_process
from mbed_greentea.mbed_greentea_log import gt_logger


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
        },
    "NRF51_DK" : {
        "yotta_targets": [
                {
                    "yotta_target": "nrf51dk-gcc",
                    "mbed_toolchain": "GCC_ARM"
                },
                {
                    "yotta_target": "nrf51dk-armcc",
                    "mbed_toolchain": "ARM"
                }
             ],
        "properties" : {
                "binary_type": "-combined.hex",
                "copy_method": "shell",
                "reset_method": "default",
                "program_cycle_s": 4
            }
        },
    "NRF51822" : {
        "yotta_targets": [
                {
                    "yotta_target": "mkit-gcc",
                    "mbed_toolchain": "GCC_ARM"
                },
                {
                    "yotta_target": "mkit-armcc",
                    "mbed_toolchain": "ARM"
                }
             ],
        "properties" : {
                "binary_type": "-combined.hex",
                "copy_method": "shell",
                "reset_method": "default",
                "program_cycle_s": 4
            }
        },
    "ARCH_BLE" : {
        "yotta_targets": [
                {
                    "yotta_target": "tinyble-gcc",
                    "mbed_toolchain": "GCC_ARM"
                }
             ],
        "properties" : {
                "binary_type": "-combined.hex",
                "copy_method": "shell",
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
    "mbed-test-serial_interrupt",
    "mbed-test-stl",
    "mbed-test-sleep_timeout",
    "mbed-test-blinky",
    "mbed-test-heap_and_stack",
    "mbed-test-cstring",
]

def get_mbed_target_from_current_dir():
    """! Function uses yotta target command to check current target
    @return Returns current target or None if target not found (e.g. not yotta package)
    """
    result = None
    cmd = ['yotta', '--plain', 'target']
    gt_logger.gt_log("checking yotta target in current directory")
    gt_logger.gt_log_tab("calling yotta: %s"% " ".join(cmd))
    _stdout, _stderr, _ret = run_cli_process(cmd)
    if not _ret:
        for line in _stdout.splitlines():
            target = parse_yotta_target_cmd_output(line)
            if target:
                result = target
                break
    return result

def parse_yotta_target_cmd_output(line):
    # Example targets:
    # $ yt target
    # frdm-k64f-gcc 0.1.3
    # mbed-gcc 0.1.1
    m = re.search(r'[\w\d_-]+ \d+\.\d+\.\d+', line)
    if m and len(m.group()):
        result = line.split()[0]
        return result
    return None

def get_mbed_targets_from_yotta_local_module(mbed_classic_name, yotta_targets_path='./yotta_targets'):
    """! Function is parsing local yotta targets to fetch matching mbed device target's name
    @return Function returns list of possible targets or empty list if value not found
    """
    result = []

    if os.path.exists(yotta_targets_path):
        # All local diorectories with yotta targets
        target_dirs = [target_dir_name for target_dir_name in os.listdir(yotta_targets_path) if os.path.isdir(os.path.join(yotta_targets_path, target_dir_name))]

        gt_logger.gt_log("local yotta target search in '%s' for compatible mbed-target '%s'"% (gt_logger.gt_bright(yotta_targets_path), gt_logger.gt_bright(mbed_classic_name.lower().strip())))

        for target_dir in target_dirs:
            path = os.path.join(yotta_targets_path, target_dir, 'target.json')
            try:
                with open(path, 'r') as data_file:
                    target_json_data = json.load(data_file)
                    yotta_target_name = parse_mbed_target_from_target_json(mbed_classic_name, target_json_data)
                    if yotta_target_name:
                        target_dir_name = os.path.join(yotta_targets_path, target_dir)
                        gt_logger.gt_log_tab("inside '%s' found compatible target '%s'"% (gt_logger.gt_bright(target_dir_name), gt_logger.gt_bright(yotta_target_name)))
                        result.append(yotta_target_name)
            except IOError as e:
                gt_logger.gt_log_err(str(e))
    return result

def parse_mbed_target_from_target_json(mbed_classic_name, target_json_data):
    result = None
    if target_json_data and 'keywords' in target_json_data:
        for keyword in target_json_data['keywords']:
            # Keywords with mbed-target data embedded in to identify target
            if keyword.startswith('mbed-target:'):
                mbed_target, mbed_name = keyword.split(':')
                if mbed_name.lower() == mbed_classic_name.lower():
                    # Check in case name of the target is not specified
                    if 'name' in target_json_data:
                        yotta_target_name = target_json_data['name']
                        return yotta_target_name
    return result

def get_mbed_targets_from_yotta(mbed_classic_name):
    """! Function is using 'yotta search' command to fetch matching mbed device target's name
    @return Function returns list of possible targets or empty list if value not found
    @details Example:
             $ yt search -k mbed-target:k64f target
             frdm-k64f-gcc 0.0.16: Official mbed build target for the mbed frdm-k64f development board.
             frdm-k64f-armcc 0.0.10: Official mbed build target for the mbed frdm-k64f development board, using the armcc toolchain.

             Note: Function prints on console
    """
    result = []
    cmd = ['yotta', '--plain', 'search', '-k', 'mbed-target:%s'% mbed_classic_name.lower().strip(), 'target']
    gt_logger.gt_log("yotta search for mbed-target '%s'"% gt_logger.gt_bright(mbed_classic_name.lower().strip()))
    gt_logger.gt_log_tab("calling yotta: %s"% " ".join(cmd))
    _stdout, _stderr, _ret = run_cli_process(cmd)
    if not _ret:
        for line in _stdout.splitlines():
            yotta_target_name = parse_yotta_search_cmd_output(line)
            if yotta_target_name:
                if yotta_target_name and yotta_target_name not in result:
                    result.append(yotta_target_name)
                    gt_logger.gt_log_tab("found target '%s'" % gt_logger.gt_bright(yotta_target_name))
    else:
        gt_logger.gt_log_err("calling yotta search failed!")
    return result

def parse_yotta_search_cmd_output(line):
    m = re.search('([\w\d-]+) \d+\.\d+\.\d+[$:]?', line)
    if m and len(m.groups()):
        yotta_target_name = m.groups()[0]
        return yotta_target_name
    return None

def add_target_info_mapping(mbed_classic_name, map_platform_to_yt_target=None, use_yotta_registry=False):
    """! Adds more target information to TARGET_INFO_MAPPING by searching in yotta registry
    @return Returns TARGET_INFO_MAPPING updated with new targets
    @details Note: function mutates TARGET_INFO_MAPPING
    """

    yotta_target_search = get_mbed_targets_from_yotta_local_module(mbed_classic_name)
    if use_yotta_registry:
        # We can also use yotta registry to check for target compatibility (slower)
        yotta_registry_target_search = get_mbed_targets_from_yotta(mbed_classic_name)
        yotta_target_search.extend(yotta_registry_target_search)
        yotta_target_search = list(set(yotta_target_search))    # Reduce repeated values

    # Add extra targets to already existing and detected in the system platforms
    if mbed_classic_name in map_platform_to_yt_target:
        yotta_target_search = list(set(yotta_target_search + map_platform_to_yt_target[mbed_classic_name]))

    # Check if this targets are already there
    if mbed_classic_name not in TARGET_INFO_MAPPING:
        TARGET_INFO_MAPPING[mbed_classic_name] = {
        "yotta_targets": [],
        "properties" : {
                "binary_type": ".bin",
                "copy_method": "shell",
                "reset_method": "default",
                "program_cycle_s": 6
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
                # gt_logger.gt_log_tab("discovered extra target '%s'"% new_yt_target)
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

def get_mbed_clasic_target_info(mbed_classic_name, map_platform_to_yt_target=None, use_yotta_registry=False):
    """! Function resolves meta-data information about target given as mbed classic name.
    @param mbed_classic_name Mbed classic (mbed 2.0) name e.g. K64F, LPC1768 etc.
    @param map_platform_to_yt_target User defined mapping platfrom:supported target
    @details Function first updated TARGET_INFO_MAPPING structure and later checks if mbed classic name is available in mapping structure
    @return Returns information about yotta target for specific toolchain
    """
    TARGET_INFO_MAPPING = add_target_info_mapping(mbed_classic_name, map_platform_to_yt_target, use_yotta_registry)
    return TARGET_INFO_MAPPING[mbed_classic_name] if mbed_classic_name in TARGET_INFO_MAPPING else None

def get_mbed_supported_test(mbed_test_case_name):
    """! Checks if given test case name is supported / automated
    @param mbed_test_case_name Name of the test case
    @return Returns true if test case name from mbed SDK can be automated with mbed-greentea
    """
    return mbed_test_case_name not in NOT_SUPPORTED_TESTS
