# Copyright 2015 ARM Limited, All rights reserved
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


class TestBinary:

    def __init__(self, path, flash_method):
        """

        :return:
        """
        self.path = path
        # attributes
        self.flash_method = flash_method

    def get_path(self):
        """

        :return:
        """
        return self.path


class Test:
    def __init__(self, name):
        """

        :param name:
        :return:
        """
        self.name = name
        self.binaries = []

    def get_name(self):
        """

        :return:
        """
        return self.name

    def get_binaries(self):
        """

        :return:
        """
        return self.binaries

    def parse(self, test_json):
        """

        :param test_json:
        :return:
        """
        print test_json
        for _, binary in test_json['binaries'].iteritems():
            tb = TestBinary(binary['path'], binary['flash_method'])
            self.binaries.append(tb)


class TestBuild:

    def __init__(self, platform, toolchain, baud_rate, base_path):
        """

        :param platform:
        :param toolchain:
        :return:
        """
        self.platform = platform
        self.toolchain = toolchain
        self.baud_rate = baud_rate
        self.base_path = base_path
        self.tests = {}

    def get_name(self):
        """

        :return:
        """
        return "%s-%s" % (self.platform, self.toolchain)

    def get_platform(self):
        """

        :return:
        """
        return self.platform

    def get_toolchain(self):
        """

        :return:
        """
        return self.toolchain

    def get_baudrate(self):
        """

        :return:
        """
        return self.baud_rate

    def get_path(self):
        """

        :return:
        """
        return self.base_path

    def get_tests(self):
        """

        :return:
        """
        return self.tests

    def parse(self, target_spec):
        """

        :param target_spec:
        :return:
        """
        import json
        print json.dumps(target_spec['tests'], indent=4)
        for name, test_json in target_spec['tests'].iteritems():
            test = Test(name)
            test.parse(test_json)
            self.tests[name] = test


class TestSpec:

    def __init__(self):
        """

        :return:
        """
        self.target_test_spec = {}

    def parse(self, spec):
        """

        :param spec:
        :return:
        """
        for _, build in spec['builds'].iteritems():
            ts = TestBuild(build['platform'], build['toolchain'], build['baud_rate'], build['base_path'])
            ts.parse(build)
            self.target_test_spec["%s-%s" % (build['platform'], build['toolchain'])] = ts

    def get_test_builds(self):
        """

        :return:
        """
        return self.target_test_spec.values()
