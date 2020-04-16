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
import sys
from distutils.core import setup
from setuptools import find_packages

DESCRIPTION = "The tools to build, test, and work with Mbed OS"
OWNER_NAMES = "Jimmy Brisson, Brian Daniels"
OWNER_EMAILS = "jimmy.brisson@arm.com, brian.daniels@arm.com"

repository_dir = os.path.dirname(__file__)


def read(fname):
    """
    Utility function to cat in a file (used for the README)
    @param fname: the name of the file to read,
    relative to the directory containing this file
    @return: The string content of the opened file
    """
    with open(os.path.join(repository_dir, fname), mode='r') as f:
        return f.read()


with open(os.path.join(repository_dir, 'requirements.txt')) as fh:
    requirements = fh.readlines()

# soupsieve is not a direct requirement of this package, but left to it's own
# devices a version >= 2.0 is installed for Python 2 which is not compatible.
# Therefore perform the installation of a compatible package before any other
# packages are installed.
if sys.version_info.major == 2:
    requirements.insert(0, "soupsieve<2.0")

with open(os.path.join(repository_dir, 'test_requirements.txt')) as fh:
    test_requirements = fh.readlines()

python_requires = '>=2.7.10, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4'
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
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Embedded Systems',
    ),
    python_requires=python_requires,
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require={
        "pyocd": ["pyocd==0.14.0"]
    },
)
