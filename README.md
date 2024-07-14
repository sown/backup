# SOWN Backup

This is SOWN's backup system, currently deployed on `backup-b32-1` and `backup-b53-1`. On those servers you can find all backups in `/data`, with snapshots exposed in `/data/{hostname}/.zfs/snapshots/`.

It automatically takes backups of all hosts in Netbox with the `Backup` tag, doing the following:
- creating a zfs dataset `data/{hostname}`
- rsyncing the server's rootfs to there
  - excluding a list of standard files/directories in `excludes.py`
  - excluding any files/directories listed in `/etc/backup-exclude.conf` on the server being backed up
- taking and rotating ZFS snapshots at regular intervals, keeping as many as are needed per `config.py`
- notifying Icinga about backup completion via passive checks

## Operational notes

### Logs
All logs go to syslog, and when running from cron, errors will be emailed to SOWN.

To get full logs from journald:
```console
root@backup:~# journalctl -e _COMM=backup
```

### Manually taking a backup
About to do something dangerous? You can manually kick off a backup and a snapshot to make sure it's kept. Eg:
```console
root@backup:~# backup --quiet vpn
root@backup:~# zfs snapshot data/vpn@tds-before-18.04-upgrade
```
(skip the --quiet if you want to see logs as the backup takes place)

To delete a snapshot you made by hand:
```console
root@backup:~# zfs destroy data/vpn@tds-before-18.04-upgrade
```
## Internal details
### Hook scripts
Before running a backup, all executable files in `/etc/backup-scripts/` will be run via `run-parts`.

Hook scipts should confirm success via exit codes - if a non-zero exit code is returned, the backup script will generate an error (which will turn into a cron mail and an icinga alert). As there are multiple backup servers that run independently, hook scripts also need to be able to cope with being run multiple times at once.

`/var/lib/backup/` is created by ansible and is a safe place to store backup files so they will only be readable by root. Any backup scripts that are used on multiple servers should be deployed via ansible.

A simple example:
```bash
#!/bin/bash
set -eo pipefail
# back up the date, very important!
date > /var/lib/backup/date.$$
mv /var/lib/backup/date.$$ /var/lib/backup/date
```

### Installing
Before starting, you'll need a zfs pool called `data`. Eg on an ubuntu install, using an LVM LV for the backing block device:
```console
root@backup:~# apt install zfsutils-linux
root@backup:~# zpool create -o ashift=12 -O compression=lz4 data /dev/ubuntu-vg/data
```

Then clone the repo, create a virtual environment and install it:
```console
root@backup:~# mkdir -p /opt/sown
root@backup:~# git -C /opt/sown/ clone git@github.com:sown/backup.git
root@backup:~# cd /opt/sown/backup/
root@backup:/opt/sown/backup# python3 -m venv venv
root@backup:/opt/sown/backup# ./venv/bin/pip3 install .
```

Write a config:
```console
root@backup:/opt/sown/backup# cp backup/config.example.py backup/config.py
root@backup:/opt/sown/backup# vim backup/config.py 
```

You can then run it like so:
```console
root@backup:/opt/sown/backup# ./venv/bin/backup 
```

To make the "backup" command work system-wide:
```console
root@backup:/opt/sown/backup# ln -rs ./venv/bin/backup /usr/local/bin/
```

Once everything is up and running, add something like this to root's crontab:
```
# nightly backup
@daily /opt/sown/backup/venv/bin/backup --quiet all
```

### Developing
As the module is installed in editable mode, you can work on the source directly. To add dependencies, edit pyproject.toml, and run poetry update.

Poetry is used to manage dependencies, and you will need it to update or add dependencies.

You do not need poetry to install the tool or develop it.

#### Linting

We use `ruff` to ensure that our code meets the `PEP 8` standards.

Execute the linter: ``make lint``

#### Static Type Checking

We use `mypy` to statically type check our code.

Execute Type Checking: ``make type``
