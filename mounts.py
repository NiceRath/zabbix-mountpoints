#!/usr/bin/python3

from time import time
from pathlib import Path
from sys import argv as sys_argv
from sys import exit as sys_exit
from json import dumps as json_dumps
from os import remove as remove_file
from os import listdir
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe

ZBX_KEY_SRC = '{#MOUNT_SRC}'
ZBX_KEY_DST = '{#MOUNT_DST}'
DISCOVER_REGEX = 'cifs|nfs|fuse'
MOUNTPOINT = None

try:
    CHECK = sys_argv[1]

    if CHECK not in ['discover', 'read', 'write', 'up']:
        raise ValueError

    if CHECK != 'discover':
        MOUNTPOINT = sys_argv[2]
        if not Path(MOUNTPOINT).is_dir():
            raise ValueError

except (ValueError, IndexError):
    raise SystemExit(
        'You must specify the following arguments:\n'
        '1 => check (discover, up)\n'
        "2 => mountpoint (if check != 'discover')"
    )

if CHECK == 'discover':
    result = {'data': []}

    with subprocess_popen(
        [f"cat /etc/fstab | grep -E '{DISCOVER_REGEX}' | grep -v 'noauto' | cut -d ' ' -f-2"],
        shell=True,
        stdout=subprocess_pipe,
        stderr=subprocess_pipe,
    ) as ps:
        stdout, _ = ps.communicate()

    for line in stdout.decode('utf-8').split('\n'):
        try:
            src, dst = line.split(' ', 1)
            result['data'].append({ZBX_KEY_SRC: src, ZBX_KEY_DST: dst})

        except ValueError:
            continue

    print(json_dumps(result))

else:
    if MOUNTPOINT is None:
        print('NO MOUNTPOINT PROVIDED')
        sys_exit(1)

    with subprocess_popen(
        [f"mount | grep -c '{MOUNTPOINT}'"],
        shell=True,
        stdout=subprocess_pipe,
        stderr=subprocess_pipe,
    ) as ps:
        stdout, _ = ps.communicate()

    try:
        if stdout.decode('utf-8').strip() == '0':
            # not mounted
            print(0)

        elif CHECK == 'up':
            print(1)

        elif CHECK == 'read':
            if len(listdir(MOUNTPOINT)) > 0:
                print(1)

            else:
                print(0)

        elif CHECK == 'write':
            testfile = f'{MOUNTPOINT}/.zbx_{time()}.txt'
            with open(testfile, 'w', encoding='utf-8') as f:
                f.write('test')

            remove_file(testfile)
            print(1)

    except PermissionError:
        print(f'Zabbix Serviceuser has no permission to {CHECK} on mountpoint {MOUNTPOINT}')
        sys_exit(1)

sys_exit(0)

