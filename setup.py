"""
This module defines the attributes of the
PyPI package for the mbed SDK test suite ecosystem tools
"""

import os
from distutils.core import setup
from setuptools import find_packages

DESCRIPTION = "Host tests module with extracted from mbed SDK 2.0 workspace_tools/host_tests. Decoupling for mbed 2.0 and 3.0 common use cases."
OWNER_NAMES = 'Przemyslaw Wirkus'
OWNER_EMAILS = 'Przemyslaw.Wirkus@arm.com'


# Utility function to cat in a file (used for the README)
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='mbed-host-tests',
      version='0.1.3',
      description=DESCRIPTION,
      long_description=read('README.md'),
      author=OWNER_NAMES,
      author_email=OWNER_EMAILS,
      maintainer=OWNER_NAMES,
      maintainer_email=OWNER_EMAILS,
      url='https://github.com/mbedmicro/mbed',
      packages=find_packages(),
      license="Apache-2.0",
      install_requires=["PySerial>=2.7"])
