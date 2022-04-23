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

import re


RHEL_FAMILY_RE = re.compile(r'^(almalinux|centos|rhel|rocky)([0-9]+)$')


def is_compatible_os(archive_os: str, target_os: str) -> bool:
    """
    Check if two combinations of OS name and version are compatible.

    >>> is_compatible_os('centos7', 'centos8')
    False
    >>> is_compatible_os('centos7', 'centos7')
    True
    >>> is_compatible_os('almalinux7', 'rhel7')
    True
    >>> is_compatible_os('rocky8', 'almalinux8')
    True
    >>> is_compatible_os('ubuntu20.04', 'centos8')
    False
    """
    rhel_like1 = RHEL_FAMILY_RE.match(archive_os)
    rhel_like2 = RHEL_FAMILY_RE.match(target_os)
    if rhel_like1 and rhel_like2 and rhel_like1.group(2) == rhel_like2.group(2):
        return True
    return archive_os == target_os
