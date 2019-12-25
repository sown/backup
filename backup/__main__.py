"""SOWN Backup script."""
import logging
import subprocess

from pynetbox.api import Api

from .config import NETBOX_URL
from .logging import logger_setup
from .rotation import do_rotation
from .zfs import dataset_create, dataset_exists, dataset_mount, dataset_mounted

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
            do_rotation(dataset)
        else:
            logger.error(f"{backup} backup failed with:")
            logger.error(rsync.stdout.decode('utf-8'))
