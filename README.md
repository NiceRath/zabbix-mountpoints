# Zabbix Network-Mount Monitoring

## Install

* Copy the script `mounts.py` to the target system (*executable by the zabbix user*)
* Copy the userparameter to the target system
* Restart the Zabbix Agent service
* Import the Template on your Zabbix Server

----

## Testing

On the target system:

```bash
root@SRV1:~$ su zabbix --login --shell /bin/bash

zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/mounts.py discover
> {"data": [{"{#MOUNT_SRC}": "<REMOTE>:/test", "{#MOUNT_DST}": "/mnt/test/nfs"}, {"{#MOUNT_SRC}": "//<REMOTE>/test", "{#MOUNT_DST}": "/mnt/smb/test"}]}

zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/mounts.py up /mnt/test/nfs
> 1

zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/mounts.py read /mnt/test/nfs
> 1

zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/mounts.py write /mnt/test/nfs
> 1

# if the serviceuser has no permission on the target directory; it fails
zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/mounts.py write /mnt/test/smb
> Zabbix Serviceuser has no permission to write on mountpoint /mnt/test/smb
```

----

## Usage

You might want to grant the Zabbix Serviceuser at least read-permissions on the directory. I've seen that SMB shares are mounted, but neither read- nor writable.

The writable-check is disabled in by default (*in the template*) - enable it if needed.

Lower the check period if needed. (*default = 5min*)

Extend the `DISCOVER_REGEX` inside the script if you want to discover other types than `cifs|nfs|fuse`.

----

## Items

These are discovered dynamically by parsing `/etc/fstab`.

* Mountpoint UP/Mounted
* Mountpoint Readable
* Mountpoint Writable (*disabled by default*)

### Triggers

* Mountpoint not Mounted (*high*)
  * Mountpoint not Readable (*avg*)
  * Mountpoint not Writable (*avg - disabled by default*)
