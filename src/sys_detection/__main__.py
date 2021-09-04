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


"""
Identifies various parameters about the system.
"""

import argparse
from sys_detection import local_sys_conf


def main() -> None:
    arg_parser = argparse.ArgumentParser(__doc__)
    arg_parser.parse_args()
    sys_conf = local_sys_conf()
    print(sys_conf.id_for_packaging())


if __name__ == '__main__':
    main()
