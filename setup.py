# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
This module defines the attributes of the
PyPI package for the mbed SDK test suite ecosystem tools
"""

import os
from distutils.core import setup
from setuptools import find_packages

DESCRIPTION = "Command line tools used to detect connected mbed-enabled devices. See http://mbed.org for details"
OWNER_NAMES = 'Przemyslaw Wirkus, Johan Seferidis'
OWNER_EMAILS = 'Przemyslaw.Wirkus@arm.com, Johan.Seferidis@arm.com'


# Utility function to cat in a file (used for the README)
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='mbed-ls',
      version='0.1.8',
      description=DESCRIPTION,
      long_description=read('README.md'),
      author=OWNER_NAMES,
      author_email=OWNER_EMAILS,
      maintainer=OWNER_NAMES,
      maintainer_email=OWNER_EMAILS,
      url='https://github.com/mbedmicro/mbed',
      packages=find_packages(),
      license="Apache-2.0",
      entry_points={
        "console_scripts": [
            "mbedls=mbed_lstools:mbedls_main",
        ],
      },
      install_requires=["PrettyTable>=0.7.2"])
