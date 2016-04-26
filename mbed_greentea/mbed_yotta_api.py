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

Author: Przemyslaw Wirkus <Przemyslaw.wirkus@arm.com>
"""

from mbed_greentea.mbed_test_api import run_cli_command
from mbed_greentea.mbed_greentea_log import gt_logger
from mbed_greentea.mbed_yotta_module_parse import YottaModule
from mbed_greentea.mbed_target_info import get_mbed_target_from_current_dir


def build_with_yotta(yotta_target_name, verbose = False, build_to_release = False, build_to_debug = False):
    cmd = ["yotta"] # "yotta %s --target=%s,* build"
    if verbose:
        cmd.append("-v")
    cmd.append("--target=%s,*"% yotta_target_name)
    cmd.append("build")
    if build_to_release:
        cmd.append("-r")
    elif build_to_debug:
        cmd.append("-d")

    gt_logger.gt_log("building your sources and tests with yotta...")
    gt_logger.gt_log_tab("calling yotta: %s"% (" ".join(cmd)))
    yotta_result, yotta_ret = run_cli_command(cmd, shell=False, verbose=verbose)
    if yotta_result:
        gt_logger.gt_log("yotta build for target '%s' was successful"% gt_logger.gt_bright(yotta_target_name))
    else:
        gt_logger.gt_log_err("yotta build failed!")
    return yotta_result, yotta_ret


def get_test_spec_from_yt_module(opts):
    """

    :return:
    """
    ### Read yotta module basic information
    yotta_module = YottaModule()
    yotta_module.init() # Read actual yotta module data

    # Check if NO greentea-client is in module.json of repo to test, if so abort
    if not yotta_module.check_greentea_client():
        gt_logger.gt_log("""
        *****************************************************************************************
        * We've noticed that NO 'greentea-client' module is specified in                        *
        * dependency/testDependency section of this module's 'module.json' file.                *
        *                                                                                       *
        * This version of Greentea requires 'greentea-client' module.                           *
        * Please downgrade to Greentea before v0.2.0:                                           *
        *                                                                                       *
        * $ pip install "mbed-greentea<0.2.0" --upgrade                                         *
        *                                                                                       *
        * or port your tests to new Async model: https://github.com/ARMmbed/greentea/pull/78    *
        *****************************************************************************************
        """)
        return (0)

    ### Selecting yotta targets to process
    yt_targets = [] # List of yotta targets specified by user used to process during this run
    if opts.list_of_targets:
        yt_targets = opts.list_of_targets.split(',')
    else:
        # Trying to use locally set yotta target
        gt_logger.gt_log("checking for yotta target in current directory")
        gt_logger.gt_log_tab("reason: no --target switch set")
        current_target = get_mbed_target_from_current_dir()
        if current_target:
            gt_logger.gt_log("assuming default target as '%s'"% gt_logger.gt_bright(current_target))
            # Assuming first target printed by 'yotta search' will be used
            yt_targets = [current_target]
        else:
            gt_logger.gt_log_tab("yotta target in current directory is not set")
            gt_logger.gt_log_err("yotta target is not specified. Use '%s' or '%s' command to set target"%
            (
                gt_logger.gt_bright('mbedgt -t <yotta_target>'),
                gt_logger.gt_bright('yotta target <yotta_target>')
            ))
            return (-1)

    ### Use yotta to search mapping between platform names and available platforms
    # Convert platform:target, ... mapping to data structure
    map_platform_to_yt_target = {}
    if opts.map_platform_to_yt_target:
        gt_logger.gt_log("user defined platform -> target supported mapping definition (specified with --map-target switch)")
        p_to_t_mappings = opts.map_platform_to_yt_target.split(',')
        for mapping in p_to_t_mappings:
            if len(mapping.split(':')) == 2:
                platform, yt_target = mapping.split(':')
                if platform not in map_platform_to_yt_target:
                    map_platform_to_yt_target[platform] = []
                map_platform_to_yt_target[platform].append(yt_target)
                gt_logger.gt_log_tab("mapped platform '%s' to be compatible with '%s'"% (
                    gt_logger.gt_bright(platform),
                    gt_logger.gt_bright(yt_target)
                ))
            else:
                gt_logger.gt_log_tab("unknown format '%s', use 'platform:target' format"% mapping)

