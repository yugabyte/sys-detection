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
import platform
import shlex
import re

from typing import Optional, Any, Dict, Optional, List

from autorepr import autorepr  # type: ignore

from sys_detection.os_compatibility import is_compatible_os


VALID_ATTR_RE = re.compile('^[a-z_]+$')

SHORT_LINUX_OS_NAMES = [
    'almalinux',
    'alpine',
    'centos',
    'debian',
    'fedora',
    'ol',
    'rocky',
    'ubuntu',
    'opensuse-leap',
    'opensuse-tumbleweed',
    'arch',
    'manjaro',
    'amzn'
]

SHORT_OS_NAMES = ['macos'] + SHORT_LINUX_OS_NAMES

SHORT_OS_NAME_REGEX_STR = '|'.join(SHORT_OS_NAMES)

REDHAT_FAMILY_OS_NAMES = ['almalinux', 'centos', 'rhel', 'rocky', 'ol']
REDHAT_FAMILY_OS_NAMES_RE_STR = '|'.join(REDHAT_FAMILY_OS_NAMES)
REDHAT_FAMILY_OS_AND_VERSION_NAME_RE = re.compile(
    f'^({REDHAT_FAMILY_OS_NAMES_RE_STR})([0-9]+)$')


def read_file(file_path: str) -> str:
    with open(file_path) as input_file:
        return input_file.read()


def is_compatible_os_and_version(os_and_version1: str, os_and_version2: str) -> bool:
    """
    Determines if the two operating system name and version strings are compatible.
    >>> is_compatible_os_and_version('centos7', 'ol8')
    False
    >>> is_compatible_os_and_version('centos8', 'almalinux8')
    True
    >>> is_compatible_os_and_version('ubuntu18.04', 'ubuntu18.04')
    True
    >>> is_compatible_os_and_version('ubuntu18.04', 'ubuntu20.04')
    False
    """
    rhel_like1 = REDHAT_FAMILY_OS_AND_VERSION_NAME_RE.match(os_and_version1)
    rhel_like2 = REDHAT_FAMILY_OS_AND_VERSION_NAME_RE.match(os_and_version2)
    if rhel_like1 and rhel_like2 and rhel_like1.group(2) == rhel_like2.group(2):
        return True
    return os_and_version1 == os_and_version2


def parse_value(s: str) -> str:
    """
    >>> parse_value('"a"')
    'a'
    >>> parse_value('"CentOS Linux"')
    'CentOS Linux'
    >>> parse_value('Hello World')
    'Hello World'
    """
    tokens = list(shlex.shlex(s, posix=True))
    if len(tokens) == 1:
        return tokens[0]
    return s


class OsReleaseVars:
    # Maps lowercase versions of keys in /etc/os-release to their values.
    vars: Dict[str, str]

    id: str
    version_id: str

    def __init__(self, vars: Dict[str, str]) -> None:
        self.vars = vars
        for k, v in self.vars.items():
            if VALID_ATTR_RE.match(k):
                setattr(self, k, v)

    def __repr__(self) -> str:
        return repr(self.vars)

    __str__ = __repr__

    @staticmethod
    def read_file(file_path: str) -> 'OsReleaseVars':
        vars: Dict[str, str] = {}
        with open(file_path) as input_file:
            for line in input_file:
                line = line.strip()
                if not line:
                    continue
                items = line.split('=', 1)
                vars[items[0].lower()] = parse_value(items[1])
        return OsReleaseVars(vars)

    def get(self, k: str) -> Optional[str]:
        return self.vars.get(k)


class SysConfiguration:
    system: str
    architecture: str
    linux_os_release: Optional[OsReleaseVars]
    redhat_release: Optional[str]

    __repr__ = __str__ = autorepr(["system", "architecture", "linux_os_release"])

    ID_COMPONENT_SEPARATOR = '-'

    def __init__(
            self,
            system: str,
            architecture: str,
            linux_os_release: Optional[OsReleaseVars],
            redhat_release: Optional[str]):
        self.system = system
        self.architecture = architecture
        self.linux_os_release = linux_os_release
        self.redhat_release = redhat_release

    def is_linux(self) -> bool:
        return self.system == 'Linux'

    def is_macos(self) -> bool:
        return self.system == 'Darwin'

    def is_redhat_family(self) -> bool:
        return self.is_linux() and bool(self.redhat_release)

    @staticmethod
    def from_etc_dir(
            system: str,
            architecture: str,
            etc_dir_path: str) -> 'SysConfiguration':
        linux_os_release: Optional[OsReleaseVars] = None
        redhat_release: Optional[str] = None
        if system == 'Linux':
            os_release_path = os.path.join(etc_dir_path, 'os-release')
            linux_os_release = OsReleaseVars.read_file(os_release_path)
            redhat_release_path = os.path.join(etc_dir_path, 'redhat-release')
            if os.path.isfile(redhat_release_path):
                redhat_release = read_file(redhat_release_path).strip()
                if len(redhat_release) == 0:
                    redhat_release = None
            else:
                redhat_release = None
        return SysConfiguration(
            system=system,
            architecture=architecture,
            linux_os_release=linux_os_release,
            redhat_release=redhat_release)

    _local_system_instance: Optional['SysConfiguration'] = None

    @staticmethod
    def from_local_system(base_dir: str = '/') -> 'SysConfiguration':
        if SysConfiguration._local_system_instance is not None:
            return SysConfiguration._local_system_instance
        local_system_instance = SysConfiguration.from_etc_dir(
            system=platform.system(),
            architecture=platform.machine(),
            etc_dir_path=os.path.join(base_dir, 'etc'))
        SysConfiguration._local_system_instance = local_system_instance
        return local_system_instance

    def short_os_name(self) -> Optional[str]:
        """
        Returns a short platform name such as centos, ubuntu, macos, etc.
        """
        if self.is_macos():
            return 'macos'

        if self.is_linux():
            assert self.linux_os_release is not None
            return self.linux_os_release.id

        raise ValueError("Unrecognized platform: %s" % self)

    def short_os_version(self) -> str:
        if not self.is_linux():
            # TODO: short version strings for macOS.
            return ''

        assert self.linux_os_release is not None
        version_id: Optional[str] = self.linux_os_release.get('version_id')
        if version_id is None:
            # E.g. rolling distros do not have a version.
            return ''

        if self.is_redhat_family():
            # For RedHat family, only keep the major version.
            num_version_components = 1
        else:
            # For OSes like Ubuntu and Alpine, keep two components, like 20.04 or 3.14.
            num_version_components = 2

        return '.'.join(version_id.split('.')[:num_version_components])

    def short_os_name_and_version(self) -> str:
        return '%s%s' % (self.short_os_name(), self.short_os_version())

    def id_for_packaging(
            self,
            mid_part: List[str] = [],
            separator: str = ID_COMPONENT_SEPARATOR) -> str:
        '''
        An identifier suitable for use as a file name during packaging.
        :param mid_part: Additional components to insert in the middle of the identifier,
            between the operating system and the architecture architecture.
        :param separator: The separator to use for identifier components.
        '''
        return separator.join(
            [self.short_os_name_and_version()] + mid_part + [self.architecture]
        )


def local_sys_conf() -> SysConfiguration:
    return SysConfiguration.from_local_system()


def is_macos() -> bool:
    return local_sys_conf().is_macos()


def is_linux() -> bool:
    return local_sys_conf().is_linux()
