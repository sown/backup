This is SOWN's (in development) backup system, currently deployed on `backup-test`.

It automatically takes backups of all hosts in Netbox with the `Backup` tag, doing the following:
- creating a zfs dataset `data/{hostname}`
- rsyncing the server's rootfs to there
  - excluding a list of standard files/directories in `excludes.py`
  - excluding any files/directories listed in `/etc/backup-exclude.conf` on the server being backed up
- taking and rotating ZFS snapshots at regular intervals, keeping as many as are needed per `config.py`
- notifying Icinga about backup completion for passive checks

You can find all backups in `/data`, with snapshots exposed in `/data/{hostname}/.zfs/snapshots/`.

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
root@backup-test:/opt/sown/backup# ./venv/bin/flake8 backup
```
