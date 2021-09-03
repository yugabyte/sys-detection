#!/usr/bin/env python3

import os
import subprocess
import pathlib
import sys

from collections import defaultdict

from typing import Any, Dict, List, Union, Iterable


FILE_CONTENT_HEADER = '--- Contents of file: '
END_OF_FILE_HEADER = '--- End of file contents'
SPECIAL_MESSAGE_HEADER = '--- Message: '

VERSIONS_BY_OS: Dict[str, Iterable[Union[int, str]]] = {
    'centos': range(6, 9),
    'ubuntu': [
        '18.04', '18.10',
        '19.04', '19.10',
        '20.04', '20.10',
        '21.04'
    ],
    'almalinux': [8],
    'rockylinux': [8],
    'debian': range(8, 12),
    'alpine': ['3.%d' % i for i in range(11, 15)],
    'fedora': range(33, 36),
    'oraclelinux': range(6, 9)
}


def get_docker_tag(os_name: str, os_version: Any) -> str:
    tag_prefix = os_name
    if os_name == 'rockylinux':
        tag_prefix = '%s/%s' % (os_name, os_name)
    return '%s:%s' % (tag_prefix, os_version)


def main() -> None:
    test_data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'tests',
        'sys_detection_test',
        'test_data'
    )
    for os_name, os_versions in VERSIONS_BY_OS.items():
        for os_version in os_versions:
            docker_tag = get_docker_tag(os_name, os_version)
            output_dir = os.path.join(test_data_dir, '%s%s' % (os_name, os_version))

            print("Docker tag: %s" % docker_tag)
            output = subprocess.check_output([
                'docker', 'run', '-it', docker_tag,
                'sh', '-c',
                f'''
                files=$( ls /etc/*release* /etc/*version* )
                for file_path in $files; do
                  if [ -f $file_path ]; then
                    echo "{FILE_CONTENT_HEADER}$file_path"
                    cat "$file_path"
                    echo "{END_OF_FILE_HEADER}"
                  else
                    echo "{SPECIAL_MESSAGE_HEADER}File $file_path does not exist"
                  fi
                done
                '''
            ]).decode('utf-8')
            file_path = None
            lines_by_file = defaultdict(list)
            messages = []
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith(FILE_CONTENT_HEADER):
                    file_path = line[len(FILE_CONTENT_HEADER):]
                elif line == END_OF_FILE_HEADER:
                    file_path = None
                elif line.startswith(SPECIAL_MESSAGE_HEADER):
                    messages.append(line[len(SPECIAL_MESSAGE_HEADER):])
                elif file_path is not None:
                    lines_by_file[file_path].append(line)
                elif (line.startswith('ls: cannot access') or
                        line.endswith(': No such file or directory')):
                    pass
                elif line:
                    raise ValueError("Unrecognized line: %s" % line)
            if len(lines_by_file) == 0:
                sys.stderr.write(output)
                raise RuntimeError("No OS version files found for docker tag %s" % docker_tag)
            for file_path, lines in lines_by_file.items():
                assert file_path.startswith('/')
                full_path = os.path.join(output_dir, file_path[1:])
                pathlib.Path(os.path.dirname(full_path)).mkdir(parents=True, exist_ok=True)
                with open(full_path, 'w') as output_file:
                    print("Writing file %s" % full_path)
                    output_file.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
