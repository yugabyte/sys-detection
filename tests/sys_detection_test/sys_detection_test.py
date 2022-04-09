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
import platform

from pathlib import Path

from sys_detection import SHORT_LINUX_OS_NAMES, SysConfiguration

from typing import Set


TEST_DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'test_data')


def read_file(path: str) -> str:
    with open(path) as input_file:
        return input_file.read()


def get_platform_conf(system: str, architecture: str, test_dir_path: Path) -> SysConfiguration:
    return SysConfiguration.from_etc_dir(
        system=system,
        architecture=architecture,
        etc_dir_path=str(test_dir_path.joinpath('etc')))


def get_expected_short_name_and_version(dir_basename: str) -> str:
    if dir_basename == 'amazonlinux':
        return 'amzn2'
    return (dir_basename.replace('oraclelinux', 'ol')
                        .replace('rockylinux', 'rocky')
                        .replace('archlinux', 'arch')
                        .replace('archbase', 'arch')
                        .replace('manjarolinux', 'manjaro')
                        .replace('amazonlinux', 'amzn'))


class TestSysDetection(unittest.TestCase):
    def test_linux_versions(self) -> None:
        test_dir_path: Path
        all_short_os_names: Set[str] = set()
        for test_dir_path in Path(TEST_DATA_DIR).glob('*'):
            if not os.path.isdir(test_dir_path):
                continue
            for architecture in ['x86_64', 'aarch64']:
                dir_basename = os.path.basename(test_dir_path)
                if dir_basename in ['centos6']:
                    # TODO: implement detecting these OSes.
                    continue

                platform_conf = get_platform_conf(
                    system='Linux', architecture=architecture, test_dir_path=test_dir_path)
                short_os_name = platform_conf.short_os_name()
                assert short_os_name is not None
                all_short_os_names.add(short_os_name)
                if short_os_name == 'opensuse-tumbleweed':
                    # OpenSUSE Tumbleweed seems to have a new version number almost every day.
                    # Not sure how to deal with that yet.
                    continue

                short_name_and_version = platform_conf.short_os_name_and_version()
                expected_short_name_and_version = get_expected_short_name_and_version(dir_basename)

                context_str = (
                    f'System configuration: {platform_conf}, test directory: {dir_basename}')

                self.assertEqual(
                    expected_short_name_and_version, short_name_and_version, context_str)
                self.assertEqual(
                    '%s-%s' % (expected_short_name_and_version, architecture),
                    platform_conf.id_for_packaging(),
                    context_str)

                # We could insert more components, like the toolchain name, in the middle.
                self.assertEqual(
                    '%s-clang11-%s' % (expected_short_name_and_version, architecture),
                    platform_conf.id_for_packaging(mid_part=['clang11']))

                # We could also change the separator.
                self.assertEqual(
                    '%s_gcc9_%s' % (expected_short_name_and_version, architecture),
                    platform_conf.id_for_packaging(mid_part=['gcc9'], separator='_'))

        for short_os_name in all_short_os_names:
            self.assertTrue(
                short_os_name in SHORT_LINUX_OS_NAMES,
                f'Unexpected short OS name (not in SHORT_LINUX_OS_NAMES): {short_os_name}')

    def test_local_system(self) -> None:
        local_platform_conf = SysConfiguration.from_local_system()
        self.assertEqual(platform.machine(), local_platform_conf.architecture)
        self.assertEqual(platform.system(), local_platform_conf.system)
        if platform.system() == 'Darwin':
            self.assertFalse(local_platform_conf.is_linux())
            self.assertTrue(local_platform_conf.is_macos())
        elif platform.system() == 'Linux':
            self.assertTrue(local_platform_conf.is_linux())
            self.assertFalse(local_platform_conf.is_macos())
        else:
            self.assertFalse(local_platform_conf.is_linux())
            self.assertFalse(local_platform_conf.is_macos())


if __name__ == '__main__':
    unittest.main()
