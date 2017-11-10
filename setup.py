"""
This module defines the attributes of the
PyPI package for the mbed SDK test suite ecosystem tools
"""

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

import os
from distutils.core import setup
from io import open
from setuptools import find_packages

DESCRIPTION = "mbed-ls is a Python module that detects and lists mbed-enabled devices connected to the host computer"
OWNER_NAMES = 'Przemyslaw Wirkus, Johan Seferidis, James Crosby'
OWNER_EMAILS = 'Przemyslaw.Wirkus@arm.com, Johan.Seferidis@arm.com, James.Crosby@arm.com'


# Utility function to cat in a file (used for the README)
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding="utf8").read()

setup(name='mbed-ls',
      version='1.3.4',
      description=DESCRIPTION,
      long_description=read('README.md'),
      author=OWNER_NAMES,
      author_email=OWNER_EMAILS,
      maintainer=OWNER_NAMES,
      maintainer_email=OWNER_EMAILS,
      url='https://github.com/ARMmbed/mbed-ls',
      packages=find_packages(),
      license="Apache-2.0",
      test_suite = 'test',
      entry_points={
        "console_scripts": [
            "mbedls=mbed_lstools:mbedls_main",
        ],
      },
      install_requires=[
          "PrettyTable>=0.7.2",
          "fasteners",
          "appdirs>=1.4"
      ],
      tests_require = [
          "mock>=2",
          "pytest>=3"
      ],
      extras_require = {
          "colorized_logs": ["colorlog"]
      }
)
