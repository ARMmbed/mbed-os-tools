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
import traceback
from time import time
from Queue import Empty as QueueEmpty   # Queue here refers to the module, not a class

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

        def callback__notify_prn(key, value, timestamp):
            """! Handles __norify_prn. Prints all lines in separate log line """
            for line in value.splitlines():
                self.logger.prn_inf(line)

        callbacks = {
            "__notify_prn" : callback__notify_prn
        }

        # if True we will allow host test to consume all events after test is finished
        callbacks_consume = True
        # Flag check if __exit event occurred
        callbacks__exit = False
        # Handle to dynamically loaded host test object
        self.test_supervisor = None
        # Version: greentea-client version from DUT
        self.client_version = None

        self.logger.prn_inf("starting host test process...")

        def start_conn_process():
            # Create device info here as it may change after restart.
            config = {
                "digest" : "serial",
                "port" : self.mbed.port,
                "baudrate" : self.mbed.serial_baud,
                "program_cycle_s" : self.options.program_cycle_s,
                "reset_type" : self.options.forced_reset_type
            }
            # DUT-host communication process
            args = (event_queue, dut_event_queue, self.prn_lock, config)
            p = Process(target=conn_process, args=args)
            p.deamon = True
            p.start()
            return p
        p = start_conn_process()

        start_time = time()

        try:
            consume_preamble_events = True
            while (time() - start_time) < timeout_duration:
                # Handle default events like timeout, host_test_name, ...
                if not event_queue.empty():
                    try:
                        (key, value, timestamp) = event_queue.get(timeout=1)
                    except QueueEmpty:
                        continue

                    if consume_preamble_events:
                        if key == '__timeout':
                            # Override default timeout for this event queue
                            start_time = time()
                            timeout_duration = int(value) # New timeout
                            self.logger.prn_inf("setting timeout to: %d sec"% int(value))
                        elif key == '__version':
                            self.client_version = value
                            self.logger.prn_inf("DUT greentea-client version: " + self.client_version)
                        elif key == '__host_test_name':
                            # Load dynamically requested host test
                            self.test_supervisor = get_host_test(value)
                            if self.test_supervisor:
                                # Pass communication queues and setup() host test
                                self.test_supervisor.setup_communication(event_queue, dut_event_queue)
                                try:
                                    # After setup() user should already register all callbacks
                                    self.test_supervisor.setup()
                                except (TypeError, ValueError):
                                    # setup() can throw in normal circumstances TypeError and ValueError
                                    self.logger.prn_err("host test setup() failed, reason:")
                                    self.logger.prn_inf("==== Traceback start ====")
                                    for line in traceback.format_exc().splitlines():
                                        print line
                                    self.logger.prn_inf("==== Traceback end ====")
                                    result = self.RESULT_ERROR
                                    break

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
                        elif key.startswith('__'):
                            # Consume other system level events
                            pass
                        else:
                            self.logger.prn_err("orphan event in preamble phase: {{%s;%s}}, timestamp=%f"% (key, str(value), timestamp))
                    else:
                        if key == '__notify_complete':
                            # This event is sent by Host Test, test result is in value
                            # or if value is None, value will be retrieved from HostTest.result() method
                            self.logger.prn_inf("%s(%s)"% (key, str(value)))
                            result = value
                            break
                        elif key == '__reset_dut':
                            # Disconnecting and re-connecting comm process will reset DUT
                            dut_event_queue.put(('__host_test_finished', True, time()))
                            p.join()
                            # self.mbed.update_device_info() - This call is commented but left as it would be required in hard reset.
                            p = start_conn_process()
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
        except Exception:
            self.logger.prn_err("something went wrong in event main loop!")
            self.logger.prn_inf("==== Traceback start ====")
            for line in traceback.format_exc().splitlines():
                print line
            self.logger.prn_inf("==== Traceback end ====")
            result = self.RESULT_ERROR

        time_duration = time() - start_time
        self.logger.prn_inf("test suite run finished after %.2f sec..."% time_duration)

        # Force conn_proxy process to return
        dut_event_queue.put(('__host_test_finished', True, time()))
        p.join()
        self.logger.prn_inf("CONN exited with code: %s"% str(p.exitcode))

        # Callbacks...
        self.logger.prn_inf("No events in queue" if event_queue.empty() else "Some events in queue")

        # If host test was used we will:
        # 1. Consume all existing events in queue if consume=True
        # 2. Check result from host test and call teardown()

        if callbacks_consume:
            # We are consuming all remaining events if requested
            while not event_queue.empty():
                try:
                    (key, value, timestamp) = event_queue.get(timeout=1)
                except QueueEmpty:
                    break

                if key == '__notify_complete':
                    # This event is sent by Host Test, test result is in value
                    # or if value is None, value will be retrieved from HostTest.result() method
                    self.logger.prn_inf("%s(%s)"% (key, str(value)))
                    result = value
                elif key.startswith('__'):
                    # Consume other system level events
                    pass
                elif key in callbacks:
                    callbacks[key](key, value, timestamp)
                else:
                    self.logger.prn_wrn(">>> orphan event: {{%s;%s}}, timestamp=%f"% (key, str(value), timestamp))
            self.logger.prn_inf("stopped consuming events")

        if result is not None:  # We must compare here against None!
            # Here for example we've received some error code like IOERR_COPY
            self.logger.prn_inf("host test result() call skipped, received: %s"% str(result))
        else:
            if self.test_supervisor:
                result = self.test_supervisor.result()
            self.logger.prn_inf("host test result(): %s"% str(result))

        if not callbacks__exit:
            self.logger.prn_wrn("missing __exit event from DUT")

        #if not callbacks__exit and not result:
        if not callbacks__exit and result is None:
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

        try:
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

        except KeyboardInterrupt:
            return(-3)    # Keyboard interrupt