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
except ImportError:
    pass

# We will check if import actually was successful
COLORAMA = 'colorama' in sys.modules


class GreenTeaSimpleLockLogger:
    """! Simple locking printing mechanism
    @details We are using parallel testing
    """
    # Colors used by colorama terminal component
    DIM = ''
    BRIGHT = ''
    GREEN = ''
    RED = ''
    BLUE = ''
    YELLOW = ''
    RESET = ''

    def __init__(self, colors=True):
        self.colors = colors    # Use colours for formatting

        # Mutext used to protect logger prints
        # Usage:
        # GREENTEA_LOG_MUTEX.acquire(1)
        # GREENTEA_LOG_MUTEX.release()
        self.GREENTEA_LOG_MUTEX = Lock()

        if not COLORAMA:
            self.gt_log("Colorful console output is disabled")
        else:
            colorama.init()
            self.DIM = colorama.Style.DIM
            self.BRIGHT = colorama.Style.BRIGHT
            self.GREEN = colorama.Fore.GREEN
            self.RED = colorama.Fore.RED
            self.BLUE = colorama.Fore.BLUE
            self.YELLOW = colorama.Fore.YELLOW
            self.RESET = colorama.Style.RESET_ALL

    def colorful(self, colors):
        """! Enable/Disable colourful printing
        """
        self.colors = colors

    def __print(self, text):
        self.GREENTEA_LOG_MUTEX.acquire(1)
        print text
        self.GREENTEA_LOG_MUTEX.release()

    def gt_log(self, text, print_text=True):
        """! Prints standard log message (in colour if colorama is installed)
        @param print_text Forces log function to print on screen (not only return message)
        @return Returns string with message
        """
        result = self.GREEN + self.BRIGHT + "mbedgt: " + self.RESET + text
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
        result = self.RED + self.BRIGHT + "mbedgt: " + self.RESET + text
        if print_text:
            self.__print(result)
        return result

    def gt_log_warn(self, text, print_text=True):
        """! Prints error log message (in color if colorama is installed)
        @param print_text Forces log function to print on screen (not only return message)
        @return Returns string with message
        """
        result = self.YELLOW + "mbedgt: " + self.RESET + text
        if print_text:
            self.__print(result)
        return result

    def gt_bright(self, text):
        """! Created bright text using colorama
        @return Returns string with additional BRIGHT color codes
        """
        if not text:
            text = ''
        return self.BLUE + self.BRIGHT + text + self.RESET

gt_logger = GreenTeaSimpleLockLogger()
