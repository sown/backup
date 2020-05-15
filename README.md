# SOWN Backup

This is SOWN's (in development) backup system, currently deployed on `backup-test`.

It automatically takes backups of all hosts in Netbox with the `Backup` tag, doing the following:
- creating a zfs dataset `data/{hostname}`
- rsyncing the server's rootfs to there
  - excluding a list of standard files/directories in `excludes.py`
  - excluding any files/directories listed in `/etc/backup-exclude.conf` on the server being backed up
- taking and rotating ZFS snapshots at regular intervals, keeping as many as are needed per `config.py`
- notifying Icinga about backup completion for passive checks

You can find all backups in `/data`, with snapshots exposed in `/data/{hostname}/.zfs/snapshots/`.

## Hook scripts
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

## Manually taking a backup
About to do something dangerous? You can manually kick off a backup and a snapshot to make sure it's kept. Eg:
```console
root@backup-test:~# backup --quiet vpn
root@backup-test:~# zfs snapshot data/vpn@tds-before-18.04-upgrade
```
(skip the --quiet if you want to see logs as the backup takes place)

To delete a snapshot you made by hand:
```console
root@backup-test:~# zfs destroy data/vpn@tds-before-18.04-upgrade
```

## Installing
To start, clone the repo, assumed to `/opt/sown/backup`. Then create a virtual environment and install it:
```console
root@backup-test:~# cd /opt/sown/backup/
root@backup-test:/opt/sown/backup# python3 -m venv venv
root@backup-test:/opt/sown/backup# ./venv/bin/pip3 install -e .[dev]
```

Write a config:
```console
root@backup-test:/opt/sown/backup# cp backup/config.example.py backup/config.py
root@backup-test:/opt/sown/backup# vim backup/config.py 
```

You can then run it like so:
```console
root@backup-test:/opt/sown/backup# ./venv/bin/backup 
```

To make the "backup" command work system-wide:
```console
root@backup-test:/opt/sown/backup# ln -rs ./venv/bin/backup /usr/local/bin/
```

## Developing
As the module is installed in editable mode, you can work on the source directly. To add dependencies, edit setup.py, and re-run the pip command above.

To run the linter:
```console
root@backup-test:/opt/sown/backup# source venv/bin/activate
(venv) root@backup-test:/opt/sown/backup# flake8 backup
```
