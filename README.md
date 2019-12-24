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
