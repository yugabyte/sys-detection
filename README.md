# sys-detection

https://pypi.org/project/sys-detection/

Allows identifiying the current operating system, which is helpful when
building and packaging cross-platform software.

## Usage as module

```
>>> from sys_detection import local_sys_conf

>>> local_sys_conf()
 <sys_detection.SysConfiguration system='Linux' architecture='x86_64' linux_os_release={'NAME': 'CentOS Stream', 'VERSION': '8', 'ID': 'centos', 'ID_LIKE': 'rhel fedora', 'VERSION_ID': '8', 'PLATFORM_ID': 'platform:el8', 'PRETTY_NAME': 'CentOS Stream 8', 'ANSI_COLOR': '0;31', 'CPE_NAME': 'cpe:/o:centos:centos:8', 'HOME_URL': 'https://centos.org/', 'BUG_REPORT_URL': 'https://bugzilla.redhat.com/', 'REDHAT_SUPPORT_PRODUCT': 'Red Hat Enterprise Linux 8', 'REDHAT_SUPPORT_PRODUCT_VERSION': 'CentOS Stream'} at 0x7f0123456789>

>>> local_sys_conf().id_for_packaging()
'centos8-x86_64'

>>> local_sys_conf().id_for_packaging(mid_part=['moreinfo'])
'centos8-moreinfo-x86_64'

>>> local_sys_conf().id_for_packaging(separator='_')
'centos8_x86_64'
```

## Command-line usage

```bash
python3 -m sys_detection
```

Output:

```
centos8-x86_64
```
