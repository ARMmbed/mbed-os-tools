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


import sys
from time import time

from multiprocessing import Process, Queue, Lock
from mbed_host_tests import print_ht_list
from mbed_host_tests import get_host_test
from mbed_host_tests import enum_host_tests
from mbed_host_tests import host_tests_plugins
from mbed_host_tests.host_tests_conn_proxy import HtrunLogger
from mbed_host_tests.host_tests_conn_proxy import conn_process
from mbed_host_tests.host_tests_runner.host_test import DefaultTestSelectorBase
from mbed_host_tests.host_tests_toolbox.host_functional import handle_send_break_cmd


class DefaultTestSelector(DefaultTestSelectorBase):
    """! Select default host_test supervision (replaced after auto detection) """

    def __init__(self, options):
        """! ctor
        """
        self.options = options

        self.prn_lock = Lock()
        self.logger = HtrunLogger(self.prn_lock, 'HTST')

        # Handle extra command from
        if options:
            if options.enum_host_tests:
                path = self.options.enum_host_tests
                enum_host_tests(path, verbose=options.verbose)

            if options.list_reg_hts:    # --list option
                print_ht_list()
                sys.exit(0)

            if options.list_plugins:    # --plugins option
                host_tests_plugins.print_plugin_info()
                sys.exit(0)

            if options.version:         # --version
                import pkg_resources    # part of setuptools
                version = pkg_resources.require("mbed-host-tests")[0].version
                print version
                sys.exit(0)

            if options.send_break_cmd:  # -b with -p PORT (and optional -r RESET_TYPE)
                handle_send_break_cmd(port=options.port,
                    disk=options.disk,
                    reset_type=options.forced_reset_type,
                    verbose=options.verbose)
                sys.exit(0)

        DefaultTestSelectorBase.__init__(self, options)

    def run_test(self):
        result = None
        timeout_duration = 10       # Default test case timeout
        event_queue = Queue()       # Events from DUT to host
        dut_event_queue = Queue()   # Events from host to DUT {k;v}

        callbacks = {
            "__notify_prn" : lambda k, v, t: self.logger.prn_inf(v)
        }

        # if True we will allow host test to consume all events after test is finished
        callbacks_consume = True
        # Flag check if __exit event occurred
        callbacks__exit = False
        # Handle to dynamically loaded host test object
        self.test_supervisor = None

        config = {
            "digest" : "serial",
            "port" : self.mbed.port,
            "baudrate" : self.mbed.serial_baud,
            "program_cycle_s" : self.options.program_cycle_s,
            "reset_type" : self.options.forced_reset_type
        }

        self.logger.prn_inf("starting host test process...")
        start_time = time()

        # DUT-host communication process
        args = (event_queue, dut_event_queue, self.prn_lock, config)
        p = Process(target=conn_process, args=args)
        p.deamon = True
        p.start()

        consume_preamble_events = True
        while (time() - start_time) < timeout_duration:
            # Handle default events like timeout, host_test_name, ...
            if event_queue.qsize():
                (key, value, timestamp) = event_queue.get()

                if consume_preamble_events:
                    if key == '__timeout':
                        # Override default timeout for this event queue
                        start_time = time()
                        timeout_duration = int(value) # New timeout
                        self.logger.prn_inf("setting timeout to: %d sec"% int(value))
                    elif key == '__host_test_name':
                        # Load dynamically requested host test
                        self.test_supervisor = get_host_test(value)
                        if self.test_supervisor:
                            # Pass communication queues and setup() host test
                            # After setup() user should already register all ccallbacks
                            self.test_supervisor.event_queue = event_queue
                            self.test_supervisor.dut_event_queue = dut_event_queue
                            self.test_supervisor.setup()
                            self.logger.prn_inf("host test setup() call...")
                            if self.test_supervisor.get_callbacks():
                                callbacks.update(self.test_supervisor.get_callbacks())
                                self.logger.prn_inf("CALLBACKs updated")
                            else:
                                self.logger.prn_wrn("no CALLBACKs specified by host test")
                            self.logger.prn_inf("host test detected: %s"% value)
                        else:
                            self.logger.prn_err("host test not detected: %s"% value)
                        consume_preamble_events = False
                    elif key == '__sync':
                        # This is DUT-Host Test handshake event
                        self.logger.prn_inf("sync KV found, uuid=%s, timestamp=%f"% (str(value), timestamp))
                    elif key == '__notify_conn_lost':
                        # This event is sent by conn_process, DUT connection was lost
                        self.logger.prn_err(value)
                        self.logger.prn_wrn("stopped to consume events due to %s event"% key)
                        callbacks_consume = False
                        result = self.RESULT_IO_SERIAL
                        break
                    else:
                        self.logger.prn_err("orphan event in preamble phase: {{%s;%s}}, timestamp=%f"% (key, str(value), timestamp))
                else:
                    if key == '__notify_complete':
                        # This event is sent by Host Test, test result is in value
                        # or if value is None, value will be retrieved from HostTest.result() method
                        self.logger.prn_inf("%s(%s)"% (key, str(value)))
                        result = value
                    elif key == '__notify_conn_lost':
                        # This event is sent by conn_process, DUT connection was lost
                        self.logger.prn_err(value)
                        self.logger.prn_wrn("stopped to consume events due to %s event"% key)
                        callbacks_consume = False
                        result = self.RESULT_IO_SERIAL
                        break
                    elif key == '__exit':
                        # This event is sent by DUT, test suite exited
                        self.logger.prn_inf("%s(%s)"% (key, str(value)))
                        callbacks__exit = True
                        break
                    elif key in callbacks:
                        # Handle callback
                        callbacks[key](key, value, timestamp)
                    else:
                        self.logger.prn_err("orphan event in main phase: {{%s;%s}}, timestamp=%f"% (key, str(value), timestamp))

        time_duration = time() - start_time
        self.logger.prn_inf("test suite run finished after %.2f sec..."% time_duration)

        p.terminate()
        self.logger.prn_inf("CONN exited with code: %s"% str(p.exitcode))

        # Callbacks...
        self.logger.prn_inf("%d events in queue"% event_queue.qsize())

        # If host test was used we will:
        # 1. Consume all existing events in queue if consume=True
        # 2. Check result from host test and call teardown()

        if callbacks_consume:
            # We are consuming all remaining events if requested
            while event_queue.qsize():
                (key, value, timestamp) = event_queue.get()
                if key in callbacks:
                    callbacks[key](key, value, timestamp)
                else:
                    self.logger.prn_wrn(">>> orphan event: {{%s;%s}}, timestamp=%f"% (key, str(value), timestamp))
            self.logger.prn_inf("stopped consuming events")

        if result is not None:  # We must compare here against None!
            # Here for example we've received some error code like IOERR_COPY
            self.logger.prn_inf("host test result() skipped, received: %s"% str(result))
        else:
            if self.test_supervisor:
                result = self.test_supervisor.result()
            self.logger.prn_inf("host test result(): %s"% str(result))

        if not callbacks__exit:
            self.logger.prn_wrn("missing __exit event from DUT")

        if not callbacks__exit and not result:
            self.logger.prn_err("missing __exit event from DUT and no result from host test, timeout...")
            result = self.RESULT_TIMEOUT

        self.logger.prn_inf("calling blocking teardown()")
        if self.test_supervisor:
            self.test_supervisor.teardown()
        self.logger.prn_inf("teardown() finished")

        return result

    def execute(self):
        """! Test runner for host test.

        @details This function will start executing test and forward test result via serial port
                 to test suite. This function is sensitive to work-flow flags such as --skip-flashing,
                 --skip-reset etc.
                 First function will flash device with binary, initialize serial port for communication,
                 reset target. On serial port handshake with test case will be performed. It is when host
                 test reads property data from serial port (sent over serial port).
                 At the end of the procedure proper host test (defined in set properties) will be executed
                 and test execution timeout will be measured.
        """
        result = self.RESULT_UNDEF

        # Copy image to device
        if self.options.skip_flashing:
            self.logger.prn_inf("copy image onto target... SKIPPED!")
        else:
            self.logger.prn_inf("copy image onto target...")
            result = self.mbed.copy_image()
            if not result:
                result = self.RESULT_IOERR_COPY
                return self.get_test_result_int(result)

        # Execute test if flashing was successful or skipped
        test_result = self.run_test()

        if test_result == True:
            result = self.RESULT_SUCCESS
        elif test_result == False:
            result = self.RESULT_FAILURE
        elif test_result is None:
            result = self.RESULT_ERROR
        else:
            result = test_result

        # This will be captured by Greentea
        self.logger.prn_inf("{{result;%s}}"% result)
        return self.get_test_result_int(result)
