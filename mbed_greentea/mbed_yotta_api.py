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
