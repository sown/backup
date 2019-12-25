"""SOWN Backup script."""
import logging
import logging.handlers
import subprocess
from datetime import datetime

from pynetbox.api import Api

from .config import NETBOX_URL
from .zfs import (
    dataset_create,
    dataset_exists,
    dataset_mount,
    dataset_mounted,
    dataset_snapshot,
)

logger = logging.getLogger(__name__)


def get_backups():
    """Get list of servers to back up from netbox."""
    nb = Api(NETBOX_URL, ssl_verify=False)

    tobackup = []

    devices = nb.dcim.devices.all()
    vms = nb.virtualization.virtual_machines.all()
    servers = devices + vms

    for server in servers:
        if "Backup" in server.tags:
            if not server.primary_ip:
                logger.error(f"{server.name} has no primary IP")
            elif not server.primary_ip.dns_name:
                logger.error(f"{server.name} has no DNS name for primary IP")
            else:
                tobackup.append(server.primary_ip.dns_name)

    return tobackup


def logger_setup(quiet):
    """Setup the logger."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    syslog = logging.handlers.SysLogHandler("/dev/log")
    syslog.setLevel(logging.INFO)

    stderr = logging.StreamHandler()
    if quiet:
        stderr.setLevel(logging.WARNING)
    else:
        stderr.setLevel(logging.INFO)

    logger.addHandler(stderr)
    logger.addHandler(syslog)


def main():
    """Do backups."""
    logger_setup(False)

    for backup in get_backups():
        dataset = f"data/{backup}"
        if not dataset_exists(dataset):
            dataset_create(dataset)
            logger.info(f"created {dataset}")
        else:
            logger.info(f"{dataset} already exists")
            if not dataset_mounted(dataset):
                dataset_mount(dataset)

        rsync = subprocess.run(["rsync",
                                "-e", "ssh -o 'StrictHostKeyChecking yes'",
                                "--one-file-system",
                                "--quiet",
                                "--archive",
                                "--delete",
                                f"{backup}:/",
                                f"/{dataset}/"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

        if rsync.returncode == 0:
            logger.info(f"{backup} backup complete.")
            snapshot = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            dataset_snapshot(dataset, snapshot)
        else:
            logger.error(f"{backup} backup failed with:")
            logger.error(rsync.stdout.decode('utf-8'))
