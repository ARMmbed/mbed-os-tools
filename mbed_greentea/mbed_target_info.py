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

NOT_SUPPORTED_TESTS = [
    "mbed-test-detect",
    "mbed-test-serial_interrupt",
    "mbed-test-stl",
    "mbed-test-sleep_timeout",
    "mbed-test-blinky",
    "mbed-test-heap_and_stack",
    "mbed-test-cstring",
]

def get_mbed_clasic_target_info(mbed_classic_name):
    """ Function resolves meta-data information about target given as mbed classic name.
        Returns information about yotta target for specific toolchain
    """
    return TARGET_INFO_MAPPING[mbed_classic_name] if mbed_classic_name in TARGET_INFO_MAPPING else None

def get_mbed_supported_test(mbed_test_case_name):
    """ returns true if test case name from mbed SDK can be automated with mbed-greentea
    """
    return mbed_test_case_name not in NOT_SUPPORTED_TESTS
