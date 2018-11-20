"""
Copyright (c) 2018, Arm Limited
SPDX-License-Identifier: Apache-2.0

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

import os
from distutils.core import setup
from io import open
from setuptools import find_packages

DESCRIPTION = "The tools to build, test, and work with Mbed OS"
OWNER_NAMES = "Jimmy Brisson, Brian Daniels"
OWNER_EMAILS = "jimmy.brisson@arm.com, brian.daniels@arm.com"


# Utility function to cat in a file (used for the README)
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding="utf8").read()


setup(
    name="mbed-tools",
    version="0.0.1",
    description=DESCRIPTION,
    long_description=read("README.md"),
    author=OWNER_NAMES,
    author_email=OWNER_EMAILS,
    maintainer=OWNER_NAMES,
    maintainer_email=OWNER_EMAILS,
    url="https://github.com/ARMmbed/mbed-tools",
    packages=find_packages(),
    license="Apache-2.0",
    test_suite="test",
    install_requires=[
        "PySerial>=3.0",
        "requests",
        "pyOCD==0.12.0",
        "intelhex",
        "future",
        "PrettyTable>=0.7.2",
        "fasteners",
        "appdirs>=1.4",
        "junit-xml",
        "lockfile",
        "six",
        "colorama>=0.3,<0.4",
    ],
    tests_require=["mock>=2", "pytest>=3"],
    extras_require={"colorized_logs": ["colorlog"]},
)
