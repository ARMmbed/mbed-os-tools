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

import os
import re
import json
from mbed_greentea.mbed_common_api import run_cli_process
from mbed_greentea.mbed_greentea_log import gt_logger


## Information about some properties of targets (platforms)
#
#  "default" entry is used to fetch "global" properties if they are not
#  specified with each platform
#

TARGET_INFO_MAPPING = {
    "default" : {
        "program_cycle_s": 4,
        "binary_type": ".bin",
        "copy_method": "default",
        "reset_method": "default"
    },

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

def get_mbed_target_call_yotta_target():
    """! Calls yotta's 'yotta target' command to get information about
    """
    cmd = ['yotta', '--plain', 'target']
    gt_logger.gt_log("checking yotta target in current directory")
    gt_logger.gt_log_tab("calling yotta: %s"% " ".join(cmd))
    _stdout, _stderr, _ret = run_cli_process(cmd)
    return _stdout, _stderr, _ret

def parse_yotta_json_for_build_name(yotta_json_content):
    """! Function parse .yotta.json to fetch set yotta target
    @param yotta_json_content Content of .yotta_json file
    @return String with set yotta target name, None if no target found
    """
    result = None
    if 'build' in yotta_json_content:
        if 'target' in yotta_json_content['build']:
            # yotta_json_content['build']['target'] should be something like this: "frdm-k64f-gcc,*"
            # We will split this string using ','. Because split will always return an array
            # with at least 1 element we can select first element to be target name
            try:
                result = yotta_json_content['build']['target'].split(',')[0]
            except IndexError:
                result = None
    return result

def get_yotta_target_from_local_config(yotta_json='.yotta.json'):
    """! Load yotta target from local configuration file
    @param yotta_json File in format of .yotta.json which stores current target names
    @return Yotta target set in currect directory, None if no info is available
    @details
    Example structure of .yotta.json file:
    {
      "build": {
        "target": "frdm-k64f-gcc,*",
        "targetSetExplicitly": true
      }
    }
    """
    result = None
    if os.path.exists(yotta_json):
        try:
            gt_logger.gt_log("parsing local file '%s' for target information"% yotta_json)
            with open(yotta_json, 'r') as f:
                result = parse_yotta_json_for_build_name(json.load(f))
        except Exception as e:
            print str(e)
    return result

def get_mbed_target_from_current_dir():
    """! Function uses yotta target command to check current target
    @return Returns current target or None if target not found (e.g. not yotta package)
    """
    # We will first try to load current target name using .yotta.json file
    result = get_yotta_target_from_local_config()

    # If we can't read .yotta.json, we will try to use command line to fetch target name
    if not result:
        _stdout, _stderr, _ret = get_mbed_target_call_yotta_target()
        if not _ret:
            for line in _stdout.splitlines():
                target = parse_yotta_target_cmd_output(line)
                if target:
                    result = target
                    break
    return result

def parse_yotta_target_cmd_output(line):
    """! Function parsed output from command 'yotta --plain target'
         looking for valid target names. First one will be used as 'default'
         of currently set yotta target
    @param line Line of text from 'yotta target' command
    @return Yotta target name, None if not parsed
    @details

    Example call to 'yotta target' command (all lines)
    $ yotta --plain target
    frdm-k64f-gcc 2.0.0
    kinetis-k64-gcc 2.2.0
    mbed-gcc 1.2.2

    """
    # Regular expression to parse stings like: 'frdm-k64f-gcc 2.0.0'
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
    @param map_platform_to_yt_target User defined mapping platform:supported target
    @details Function first updated TARGET_INFO_MAPPING structure and later checks if mbed classic name is available in mapping structure
    @return Returns information about yotta target for specific toolchain
    """
    TARGET_INFO_MAPPING = add_target_info_mapping(mbed_classic_name, map_platform_to_yt_target, use_yotta_registry)
    return TARGET_INFO_MAPPING[mbed_classic_name] if mbed_classic_name in TARGET_INFO_MAPPING else None

def get_binary_type_for_platform(platform):
    """
    Gives binary type for the given platform.

    :param platform:
    :return:
    """
    #return TARGET_INFO_MAPPING[platform]['properties']["binary_type"]
    return get_platform_property(platform, 'binary_type')

def get_platform_property(platform, property):
    """
    Gives platform property.

    :param platform:
    :return: property value, None if property not found
    """

    # First load from targets.json if available
    value_from_targets_json = get_platform_property_from_targets(platform, property)
    if value_from_targets_json:
        return value_from_targets_json

    # Check if info is available for a specific platform
    if platform in TARGET_INFO_MAPPING:
        if property in TARGET_INFO_MAPPING[platform]['properties']:
            return TARGET_INFO_MAPPING[platform]['properties'][property]

    # Check if default data is available
    if 'default' in TARGET_INFO_MAPPING:
        if property in TARGET_INFO_MAPPING['default']:
            return TARGET_INFO_MAPPING['default'][property]

    return None

def get_platform_property_from_targets(platform, property):
    """
    Load properties from targets.json file somewhere in the project structure

    :param platform:
    :return: property value, None if property not found
    """

    def get_platform_property_from_targets(targets, platform, property):
        """! Get a platforms's property from the target data structure in
             targets.json. Takes into account target inheritance.
        @param targets Data structure parsed from targets.json
        @param platform Name of the platform
        @param property Name of the property
        @return property value, None if property not found

        """

        result = None
        if platform in targets:
            if property in targets[platform]:
                result = targets[platform][property]
            elif 'inherits' in targets[platform]:
                result = None
                for inherited_target in targets[platform]['inherits']:
                    result = get_platform_property_from_targets(targets, inherited_target, property)

                    # Stop searching after finding the first value for the property
                    if result:
                        break

        return result

    result = None
    targets_json_path = []
    for root, dirs, files in os.walk(os.getcwd(), followlinks=True):
        ignored_dirs = ['.build', 'BUILD', 'tools']

        for ignored_dir in ignored_dirs:
            if ignored_dir in dirs:
                dirs.remove(ignored_dir)

        if 'targets.json' in files:
            targets_json_path.append(os.path.join(root, 'targets.json'))

    if not targets_json_path:
        gt_logger.gt_log_warn("No targets.json files found, using default target properties")

    for targets_path in targets_json_path:
        try:
            with open(targets_path, 'r') as f:
                targets = json.load(f)

                # Load property from targets.json
                result = get_platform_property_from_targets(targets, platform, property)

                # If a valid property was found, stop looking
                if result:
                    break
        except Exception:
            continue
    return result
