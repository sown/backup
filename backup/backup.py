"""Backup a server."""
import logging
import socket
import subprocess

import paramiko

from .excludes import STANDARD_EXCLUDES
from .icinga import passive_report
from .rotation import do_rotation
from .zfs import dataset_create, dataset_exists, dataset_mount, dataset_mounted

LOGGER = logging.getLogger(__name__)
RSYNC = "/usr/bin/rsync"


def backup_server(server: str) -> None:
    """Backup a server."""
    dataset = f"data/{server}"
    if not dataset_exists(dataset):
        dataset_create(dataset)
        LOGGER.info(f"created dataset {dataset}")
    else:
        LOGGER.info(f"dataset {dataset} already exists")
        if not dataset_mounted(dataset):
            dataset_mount(dataset)

    customexcludes = []
    sshclient = paramiko.SSHClient()
    sshclient.load_system_host_keys()
    try:
        sshclient.connect(server)
        sftpclient = sshclient.open_sftp()
        try:
            excludefile = sftpclient.open("/etc/backup-exclude.conf")
            customexcludes = excludefile.read().decode("utf-8").split("\n")
            LOGGER.info(f"Using custom excludes on {server}: {customexcludes}")
            excludefile.close()
        except FileNotFoundError:
            LOGGER.info(f"No excludes found for {server}, using standard ones only")

        (stdin, stdout, stderr) = sshclient.exec_command(
            "/bin/run-parts --report /etc/backup-scripts/ 2>&1")
        hooksrun = stdout.channel.recv_exit_status() == 0
        if not hooksrun:
            LOGGER.error(f"Hook scripts failed to run on {server} with errors:")
            LOGGER.error(stdout.read().decode("utf-8"))
        else:
            LOGGER.info(f"Hook scripts run on {server}")

        sshclient.close()

        excludes = STANDARD_EXCLUDES + customexcludes

        LOGGER.info(f"Starting rsync for {server}")
        rsync = subprocess.run([RSYNC,
                                "-e", "ssh -o 'StrictHostKeyChecking yes'",
                                # bail out if host key error, rather than prompting
                                "--compress",
                                "--one-file-system",
                                "--quiet",
                                "--archive",
                                "--delete",
                                "--delete-excluded",
                                "--exclude-from=-",
                                # read our generated exclude list from stdin
                                f"{server}:/",
                                f"/{dataset}/"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               input="\n".join(excludes),
                               encoding="utf-8")

        if rsync.returncode == 0:
            LOGGER.info(f"{server} backup complete.")
            # take and rotate snapshots now that we're done
            do_rotation(dataset)
            # tell icinga
            passive_report(
                host=server.upper(),
                service=f"BACKUP-{socket.gethostname().upper()}",
                message="Backup completed.",
                status=0,
            )
        else:
            LOGGER.error(f"{server} backup failed with:")
            LOGGER.error(rsync.stdout)

    except paramiko.ssh_exception.SSHException as e:
        LOGGER.error(f"SSHing to {server} failed:")
        LOGGER.error(repr(e))
