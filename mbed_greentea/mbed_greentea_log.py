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

import sys
from threading import Lock

try:
    import colorama
except:
    pass

COLORAMA = 'colorama' in sys.modules

DIM = ''
BRIGHT = ''
GREEN = ''
RED = ''
BLUE = ''
YELLOW = ''
RESET = ''

if not COLORAMA:
    print "mbedgt: colorful console output is disabled"
else:
    colorama.init()
    DIM = colorama.Style.DIM
    BRIGHT = colorama.Style.BRIGHT
    GREEN = colorama.Fore.GREEN
    RED = colorama.Fore.RED
    BLUE = colorama.Fore.BLUE
    YELLOW = colorama.Fore.YELLOW
    RESET = colorama.Style.RESET_ALL


class GreenTeaSimpleLockLogger:
    """! Simple locking printing mechanism
    """
    def __init__(self):
        self.GREENTEA_LOG_MUTEX = Lock()
        # GREENTEA_LOG_MUTEX.acquire(1)
        # GREENTEA_LOG_MUTEX.release()

    def __print(self, text):
        self.GREENTEA_LOG_MUTEX.acquire(1)
        print text
        self.GREENTEA_LOG_MUTEX.release()

    def gt_log(self, text, print_text=True):
        """! Prints standard log message (in color if colorama is installed)
        @param print_text Forces log function to print on screen (not only return message)
        @return Returns string with message
        """
        result = GREEN + BRIGHT + "mbedgt: " + RESET + text
        if print_text:
            self.__print(result)
        return result

    def gt_log_tab(self, text, tab_count=1):
        """! Prints standard log message with one (1) tab margin on the left
        @return Returns string with message
        """
        result = "\t"*tab_count + text
        self.__print(result)
        return result

    def gt_log_err(self, text, print_text=True):
        """! Prints error log message (in color if colorama is installed)
        @param print_text Forces log function to print on screen (not only return message)
        @return Returns string with message
        """
        result = RED + BRIGHT + "mbedgt: " + RESET + text
        if print_text:
            self.__print(result)
        return result

    def gt_log_warn(self, text, print_text=True):
        """! Prints error log message (in color if colorama is installed)
        @param print_text Forces log function to print on screen (not only return message)
        @return Returns string with message
        """
        result = YELLOW + "mbedgt: " + RESET + text
        if print_text:
            self.__print(result)
        return result

    def gt_bright(self, text):
        """! Created bright text using colorama
        @return Returns string with additional BRIGHT color codes
        """
        if not text:
            text = ''
        return BLUE + BRIGHT + text + RESET

gt_logger = GreenTeaSimpleLockLogger()
