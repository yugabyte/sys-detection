#!/usr/bin/env python3

import subprocess


VERSION_FILES = [
    '/etc/os-release',
    '/etc/lsb-release',
    '/etc/redhat-release',
    '/etc/alpine-release',
    '/etc/fedora-release',
    '/etc/debian_version'
]

VERSIONS_BY_OS = {
    'centos': range(6, 9),
    'ubuntu': [
        '18.04', '18.10',
        '19.04', '19.10',
        '20.04', '20.10',
        '21.04'
    ],
    'almalinux': [8],
    'debian': range(8, 12),
    'alpine': ['3.%d' % i for i in range(11, 15)],
    'fedora': range(33, 36)
}

def main():
    os_list = []
    
    test_data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__))
    )
    for os_name, os_versions in VERSIONS_BY_OS.items():
        for os_version in os_versions:
            docker_tag = '%s:%s' % (os_name, os_version)
            print("Docker tag: %s" % docker_tag)
            output = subprocess.check_call([
                'docker', 'run', '-it', docker_tag, 
                'sh', '-c', 
                '''
                for file_path in /etc/*{release,version}*; do 
                  if [ -f $file_path ]; then
                    echo "Contents of $file_path:"
                    cat "$file_path"
                  fi
                done
                '''
            ])


if __name__ == '__main__':
    main()
