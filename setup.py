"""
This module defines the attributes of the
PyPI package for the mbed SDK test suite
"""

import os
from distutils.core import setup
from setuptools import find_packages


LICENSE = open('LICENSE').read()
DESCRIPTION = "Test suite for mbed SDK 3.0. A set of Python scripts that can be used to test programs written on top of the mbed SDK"
OWNER_NAMES = 'przemekw, bogdanm'
OWNER_EMAILS = 'Przemyslaw.Wirkus@arm.com, Bogdan.Marinescu@arm.com'

# Utility function to cat in a file (used for the README)
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='mbed-greentea',
      version='0.0.5',
      description=DESCRIPTION,
      long_description=read('README.md'),
      author=OWNER_NAMES,
      author_email=OWNER_EMAILS,
      maintainer=OWNER_NAMES,
      maintainer_email=OWNER_EMAILS,
      url='https://github.com/mbedmicro/mbed',
      packages=find_packages(),
      license=LICENSE,
      entry_points={
        "console_scripts": ["mbedgt=mbed_greentea.mbed_greentea_cli:main",],
      },
      install_requires=["PrettyTable>=0.7.2", "PySerial>=2.7",
        "mbed-host-tests>=0.1.4", "mbed-ls>=0.1.5"])
