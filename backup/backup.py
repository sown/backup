"""Backup a server."""
import logging
import subprocess

import paramiko

from .config import ICINGA_HOSTNAME
from .excludes import STANDARD_EXCLUDES
from .icinga import passive_report
from .rotation import do_rotation
from .zfs import dataset_create, dataset_exists, dataset_mount, dataset_mounted

LOGGER = logging.getLogger(__name__)
RSYNC = "/usr/bin/rsync"


def backup_server(server: str) -> None:
    """Backup a server."""
    dataset = f"data/{server.lower()}"
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
        sshclient.connect(server.lower())
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
                                "--numeric-ids",
                                "--quiet",
                                "--archive",
                                "--delete",
                                "--delete-excluded",
                                "--exclude-from=-",
                                # read our generated exclude list from stdin
                                f"{server.lower()}:/",
                                f"/{dataset}/"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               input="\n".join(excludes),
                               encoding="utf-8")

        # also treat files disappearing during sync as a success
        # typically from monitoring systems, temporary files, etc
        if rsync.returncode == 0 or rsync.returncode == 24:
            LOGGER.info(f"{server} backup complete.")
            # take and rotate snapshots now that we're done
            do_rotation(dataset)
            # tell icinga
            passive_report(
                host=server,
                service=f"BACKUP-{ICINGA_HOSTNAME}",
                message="Backup completed.",
                status=0,
            )
        else:
            LOGGER.error(f"{server} backup failed with:")
            LOGGER.error(rsync.stdout)

    except (paramiko.ssh_exception.SSHException, TimeoutError) as e:
        LOGGER.error(f"SSHing to {server} failed:")
        LOGGER.error(repr(e))
