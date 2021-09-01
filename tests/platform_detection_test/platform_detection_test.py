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

from platform_detection import PlatformConfiguration, OsReleaseVars

from typing import Dict


TEST_DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'test_data')


def read_file(path: str) -> str:
    with open(path) as input_file:
        return input_file.read()


def get_platform_conf(system: str, processor: str, test_dir_path: Path) -> PlatformConfiguration:
    return PlatformConfiguration.from_etc_dir(
        system=system,
        processor=processor,
        etc_dir_path=str(test_dir_path.joinpath('etc')))


def get_expected_short_name_and_version(dir_basename: str) -> str:
    return dir_basename.replace('oraclelinux', 'ol').replace('rockylinux', 'rocky')


class TestPlatformDetection(unittest.TestCase):
    def test_all(self) -> None:
        test_dir_path: Path
        for test_dir_path in Path(TEST_DATA_DIR).glob('*'):
            if not os.path.isdir(test_dir_path):
                continue
            for processor in ['x86_64', 'aarch64']:
                dir_basename = os.path.basename(test_dir_path)
                if dir_basename in ['centos6']:
                    # TODO: implement detecting these OSes.
                    continue

                platform_conf = get_platform_conf(
                    system='Linux', processor=processor, test_dir_path=test_dir_path)

                short_name_and_version = platform_conf.short_os_name_and_version()
                expected_short_name_and_version = get_expected_short_name_and_version(dir_basename)

                self.assertEqual(expected_short_name_and_version, short_name_and_version)
                self.assertEqual(
                    '%s-%s' % (expected_short_name_and_version, processor),
                    platform_conf.id_for_packaging())


if __name__ == '__main__':
    unittest.main()
