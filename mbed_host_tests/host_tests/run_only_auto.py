"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from sys import stdout

class RunBinaryOnlyAuto():
    """ Simple, basic host test's test runner waiting for serial port
        output from MUT, no supervision over test running in MUT is executed.
    """
    def test(self, selftest):
        result = selftest.RESULT_SUCCESS
        try:
            line = ''
            while True:
                c = selftest.mbed.serial_read(512)
                if c is None:
                    return selftest.RESULT_IO_SERIAL
                stdout.write(c)
                stdout.flush()

                line += c
                if '\n' in line:
                    if '{end}' in line:
                        return None # Run executable end
                    i = line.index('\n')
                    line = line[i:]

        except KeyboardInterrupt, _:
            selftest.notify("\r\n[CTRL+C] exit")
            result = selftest.RESULT_ERROR
        return result
