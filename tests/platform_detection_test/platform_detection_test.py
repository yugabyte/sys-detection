# Copyright (c) Yugabyte, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations
# under the License.

import os
import unittest

from pathlib import Path

import os_release  # type: ignore

from platform_detection import PlatformConfiguration

TEST_DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'test_data')


def read_file(path: str) -> str:
    with open(path) as input_file:
        return input_file.read()


def get_platform_conf(system: str, processor: str, test_dir_name: str) -> PlatformConfiguration:
    return PlatformConfiguration(
        system=system,
        processor=processor,
        linux_os_release=os_release.OsRelease.read(Path(
            os.path.join(TEST_DATA_DIR, test_dir_name, 'etc', 'os-release')
        )))


class TestPlatformDetection(unittest.TestCase):
    def test_centos8_stream(self):
        platform_conf = get_platform_conf('Linux', 'x86_64 ', 'centos-stream8')
        self.assertEqual('centos', platform_conf.short_name())
        self.assertEqual('8', platform_conf.short_version())

    def test_centos7(self):
        platform_conf = get_platform_conf('Linux', 'x86_64 ', 'centos7')
        self.assertEqual('centos', platform_conf.short_name())
        self.assertEqual('7', platform_conf.short_version())

    def test_centos8(self):
        platform_conf = get_platform_conf('Linux', 'x86_64 ', 'centos8')
        self.assertEqual('centos', platform_conf.short_name())
        self.assertEqual('8', platform_conf.short_version())


if __name__ == '__main__':
    unittest.main()
