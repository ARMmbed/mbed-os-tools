# Copyright (c) 2018, Arm Limited and affiliates.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from distutils.core import setup
from setuptools import find_packages

DESCRIPTION = "The tools to build, test, and work with Mbed OS"
OWNER_NAMES = "Jimmy Brisson, Brian Daniels"
OWNER_EMAILS = "jimmy.brisson@arm.com, brian.daniels@arm.com"


# Utility function to cat in a file (used for the README)
def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), 'r') as f:
        return f.read()


setup(
    name="mbed-os-tools",
    version=read("src/mbed_os_tools/VERSION.txt").strip(),
    description=DESCRIPTION,
    long_description=read("README.md"),
    long_description_content_type='text/markdown',
    author=OWNER_NAMES,
    author_email=OWNER_EMAILS,
    maintainer=OWNER_NAMES,
    maintainer_email=OWNER_EMAILS,
    url="https://github.com/ARMmbed/mbed-os-tools",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"": ["VERSION.txt"]},
    license="Apache-2.0",
    test_suite="test",
    install_requires=[
        "PySerial>=3.0,<4.0",
        "requests>=2.0,<3.0",
        "intelhex>=2.0,<3.0",
        "future",
        "PrettyTable>=0.7.2",
        "fasteners",
        "appdirs>=1.4,<2.0",
        "junit-xml>=1.0,<2.0",
        "lockfile",
        "six>=1.0,<2.0",
        "colorama>=0.3,<0.5",
    ],
    tests_require=read("test_requirements.txt").splitlines(),
    extras_require={
        "pyocd": ["pyocd==0.14.0"]
    },
)
