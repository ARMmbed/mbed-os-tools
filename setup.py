"""
This module defines the attributes of the
PyPI package for the mbed SDK test suite ecosystem tools
"""

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

import os
from distutils.core import setup
from setuptools import find_packages

DESCRIPTION = "mbed tools used to flash, reset and supervise test execution for mbed-enabled devices"
OWNER_NAMES = 'Przemyslaw Wirkus, Azim Khan, Stefan Gutmann'
OWNER_EMAILS = 'Przemyslaw.Wirkus@arm.com, Azim.Khan@arm.com, Stefan.Gutmann@arm.com'


# Utility function to cat in a file (used for the README)
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='mbed-host-tests',
      version='1.0.0',
      description=DESCRIPTION,
      long_description=read('README.md'),
      author=OWNER_NAMES,
      author_email=OWNER_EMAILS,
      maintainer=OWNER_NAMES,
      maintainer_email=OWNER_EMAILS,
      url='https://github.com/ARMmbed/htrun',
      packages=find_packages(),
      license="Apache-2.0",
      test_suite = 'test',
      entry_points={
        "console_scripts":
            ["mbedhtrun=mbed_host_tests.mbedhtrun:main",
             "mbedflsh=mbed_host_tests.mbedflsh:main"],
      },
      install_requires=["PySerial>=3.0",
                        "PrettyTable>=0.7.2",
                        "requests",
                        "mbed-ls"])
