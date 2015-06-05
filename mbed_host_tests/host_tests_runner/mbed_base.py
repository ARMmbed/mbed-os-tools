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

# Check if 'serial' module is installed
# TODO: check in sys.modules if pySerial is installed
import json
from sys import stdout
from serial import Serial
from time import sleep, time
import mbed_host_tests.host_tests_plugins as ht_plugins

from threading import Lock


class Mbed:
    """ Base class for a host driven test
    """
    def __init__(self, options=None):
        # For compatibility with old mbed. We can use command line options for Mbed object
        # or we can pass options directly from .
        self.options = options

        self.mutex = Lock() # Used to sync access to serial port

        self.DEFAULT_RESET_TOUT = 0

        if self.options.port is None:
            raise Exception("The serial port of the target mbed have to be provided as command line arguments")

        # Options related to copy / reset mbed device
        self.port = self.options.port
        self.disk = self.options.disk
        self.image_path = self.options.image_path.strip('"') if self.options.image_path is not None else ''
        self.copy_method = self.options.copy_method
        self.program_cycle_s = float(self.options.program_cycle_s if self.options.program_cycle_s is not None else 2.0)

        self.serial = None
        self.serial_baud = 9600
        self.serial_timeout = 1

        # Test configuration in JSON format
        self.test_cfg = None
        if self.options.json_test_configuration is not None:
            try:
                print "MBED: Loading test configuration from '%s'..." % self.options.json_test_configuration
                with open(self.options.json_test_configuration) as data_file:
                    self.test_cfg = json.load(data_file)
            except IOError as e:
                print "MBED: Test configuration JSON file '{0}' I/O error({1}): {2}".format(self.options.json_test_configuration, e.errno, e.strerror)
            except:
                print "MBED: Test configuration JSON Unexpected error:"
                raise

        print 'MBED: Instrumentation: "%s" and disk: "%s"' % (self.port, self.disk)

    def init_serial_params(self, serial_baud=9600, serial_timeout=1):
        """ Initialize port parameters.
            This parameters will be used by self.init_serial() function to open serial port
        """
        self.serial_baud = serial_baud
        self.serial_timeout = serial_timeout

    def init_serial(self, serial_baud=None, serial_timeout=None):
        """ Initialize serial port.
            Function will return error is port can't be opened or initialized
        """
        # Overload serial port configuration from default to parameters' values if they are specified
        serial_baud = serial_baud if serial_baud is not None else self.serial_baud
        serial_timeout = serial_timeout if serial_timeout is not None else self.serial_timeout

        # Clear serial port
        if self.serial:
            self.serial.close()
            self.serial = None

        # We will pool for serial to be re-mounted if it was unmounted after device reset
        result = self.pool_for_serial_init(serial_baud, serial_timeout) # Blocking

        # Port can be opened
        if result:
            self.flush()
        return result

    def pool_for_serial_init(self, serial_baud, serial_timeout, pooling_loops=40, init_delay=0.5, loop_delay=0.25):
        """ Functions pools for serial port readiness
        """
        result = True
        last_error = None
        # This loop is used to check for serial port availability due to
        # some delays and remounting when devices are being flashed with new software.
        for i in range(pooling_loops):
            sleep(loop_delay if i else init_delay)
            try:
                self.serial = Serial(self.port, baudrate=serial_baud, timeout=serial_timeout)
            except Exception as e:
                result = False
                last_error = "MBED: %s"% str(e)
                stdout.write('.')
                stdout.flush()
            else:
                print "...port ready!"
                result = True
                break
        if not result and last_error:
            print last_error
        return result

    def set_serial_timeout(self, timeout):
        """ Wraps self.mbed.serial object timeout property
        """
        result = None
        if self.serial:
            self.serial.timeout = timeout
            result = True
        return result

    def serial_read(self, count=1):
        """ Wraps self.mbed.serial object read method
        """
        result = None
        self.mutex.acquire(1)
        if self.serial:
            try:
                result = self.serial.read(count)
            except:
                result = None
        self.mutex.release()
        return result

    def serial_readline(self, timeout=5):
        """ Wraps self.mbed.serial object read method to read one line from serial port
        """
        result = ''
        self.mutex.acquire(1)
        start = time()
        while (time() - start) < timeout:
            if self.serial:
                try:
                    c = self.serial.read(1)
                    result += c
                except Exception as e:
                    print "MBED: %s" % str(e)
                    result = None
                    break
                if c == '\n':
                    break
        self.mutex.release()
        return result

    def serial_write(self, write_buffer):
        """ Wraps self.mbed.serial object write method
        """
        result = None
        self.mutex.acquire(1)
        if self.serial:
            try:
                result = self.serial.write(write_buffer)
            except:
               result = None
        self.mutex.release()
        return result

    def reset_timeout(self, timeout):
        """ Timeout executed just after reset command is issued
        """
        self.mutex.acquire(1)
        for n in range(0, timeout):
            sleep(1)
        self.mutex.release()

    def reset(self):
        """ Calls proper reset plugin to do the job.
            Please refer to host_test_plugins functionality
        """
        # Flush serials to get only input after reset
        self.flush()
        if self.options.forced_reset_type:
            result = ht_plugins.call_plugin('ResetMethod', self.options.forced_reset_type, disk=self.disk)
        else:
            result = ht_plugins.call_plugin('ResetMethod', 'default', serial=self.serial)
        # Give time to wait for the image loading
        reset_tout_s = self.options.forced_reset_timeout if self.options.forced_reset_timeout is not None else self.DEFAULT_RESET_TOUT
        self.reset_timeout(reset_tout_s)
        return result

    def copy_image(self, image_path=None, disk=None, copy_method=None):
        """ Closure for copy_image_raw() method.
            Method which is actually copying image to mbed
        """
        # Set closure environment
        image_path = image_path if image_path is not None else self.image_path
        disk = disk if disk is not None else self.disk
        copy_method = copy_method if copy_method is not None else self.copy_method
        # Call proper copy method
        result = self.copy_image_raw(image_path, disk, copy_method)
        sleep(self.program_cycle_s)
        return result

    def copy_image_raw(self, image_path=None, disk=None, copy_method=None):
        """ Copy file depending on method you want to use. Handles exception
            and return code from shell copy commands.
        """
        if copy_method is not None:
            # image_path - Where is binary with target's firmware
            result = ht_plugins.call_plugin('CopyMethod', copy_method, image_path=image_path, destination_disk=disk)
        else:
            copy_method = 'default'
            result = ht_plugins.call_plugin('CopyMethod', copy_method, image_path=image_path, destination_disk=disk)
        return result;

    def flush(self):
        """ Flush serial ports
        """
        result = False
        self.mutex.acquire(1)
        if self.serial:
            self.serial.flushInput()
            self.serial.flushOutput()
            result = True
        self.mutex.release()
        return result
