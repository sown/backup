"""SOWN Backup script."""
import logging
import subprocess
from typing import List

from pynetbox.api import Api

from .config import NETBOX_URL
from .logging import logger_setup
from .rotation import do_rotation
from .zfs import dataset_create, dataset_exists, dataset_mount, dataset_mounted

LOGGER = logging.getLogger(__name__)


def get_backups() -> List[str]:
    """Get list of servers to back up from netbox."""
    LOGGER.info(f"Getting servers to backup from netbox")
    nb = Api(NETBOX_URL, ssl_verify=False)

    tobackup = []

    devices = nb.dcim.devices.all()
    vms = nb.virtualization.virtual_machines.all()
    servers = devices + vms

    for server in servers:
        if "Backup" in server.tags:
            if not server.primary_ip:
                LOGGER.error(f"{server.name} has no primary IP")
            elif not server.primary_ip.dns_name:
                LOGGER.error(f"{server.name} has no DNS name for primary IP")
            else:
                tobackup.append(server.primary_ip.dns_name)

    return tobackup


def main():
    """Do backups."""
    logger_setup(False)

    for backup in get_backups():
        dataset = f"data/{backup}"
        if not dataset_exists(dataset):
            dataset_create(dataset)
            LOGGER.info(f"created dataset {dataset}")
        else:
            LOGGER.info(f"dataset {dataset} already exists")
            if not dataset_mounted(dataset):
                dataset_mount(dataset)

        LOGGER.info(f"Starting rsync for {backup}")
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
            LOGGER.info(f"{backup} backup complete.")
            do_rotation(dataset)
        else:
            LOGGER.error(f"{backup} backup failed with:")
            LOGGER.error(rsync.stdout.decode('utf-8'))
