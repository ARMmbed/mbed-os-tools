"""
mbed SDK
Copyright (c) 2011-2014 ARM Limited

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

import sys
import threading
from mbed_host_tests import DefaultTestSelector         # Default adapter for DefaultTestSelectorBase
from mbed_host_tests import init_host_test_cli_params   # Provided command line options


def parent_monitor_thread(selector):
    """
    Monitors that parent is still connected to the child via stdin pipe. When pipe is disconnected assumes that parent
    wants it to exit. Example: in timeout situations.

    :param selector:
    :return:
    """
    while True:
        try:
            c = sys.stdin.read(1)
            if c is None or len(c) == 0:    # read returns None or empty string when stdin is closed.
                break
        except IOError:     # Error on pipe should have same behavior as stdin close.
            break
    selector.abort()    # Tell selector to abort


def main():
    """! This function drives command line tool 'mbedhtrun' which is using DefaultTestSelector

    @details 1. Create DefaultTestSelector object and pass command line parameters
             2. Call default test execution function run() to start test instrumentation
    """
    test_selector = DefaultTestSelector(init_host_test_cli_params())
    try:
        if not sys.stdin.isatty(): # Only monitor stdin if started from a parent process.
            t = threading.Thread(target=parent_monitor_thread, args=(test_selector,))
            t.start()   # This thread will shutdown automatically after stdin is closed on returning from main()
        test_selector.run()
    except (KeyboardInterrupt, SystemExit):
        test_selector.finish()
        raise
    except:
        pass
    else:
        test_selector.finish()
