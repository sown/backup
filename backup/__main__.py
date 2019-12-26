"""SOWN Backup script."""
import logging
import subprocess
from typing import List

import paramiko
from pynetbox.api import Api

from .config import NETBOX_URL
from .excludes import STANDARD_EXCLUDES
from .icinga import passive_report
from .logconfig import logger_setup
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

        customexcludes = []
        sshclient = paramiko.SSHClient()
        sshclient.load_system_host_keys()
        try:
            sshclient.connect(backup)
            sftpclient = sshclient.open_sftp()
            try:
                excludefile = sftpclient.open("/etc/backup-exclude.conf")
                customexcludes = excludefile.read().decode("utf-8").split("\n")
                LOGGER.info(f"Using custom excludes on {backup}: {customexcludes}")
                excludefile.close()
            except FileNotFoundError:
                LOGGER.info(f"No excludes found for {backup}, using standard ones only")
            sshclient.close()

            excludes = STANDARD_EXCLUDES + customexcludes

            LOGGER.info(f"Starting rsync for {backup}")
            rsync = subprocess.run(["rsync",
                                    "-e", "ssh -o 'StrictHostKeyChecking yes'",
                                    # bail out if host key error, rather than prompting
                                    "--one-file-system",
                                    "--quiet",
                                    "--archive",
                                    "--delete",
                                    "--delete-excluded",
                                    "--exclude-from=-",
                                    # read our generated exclude list from stdin
                                    f"{backup}:/",
                                    f"/{dataset}/"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   input="\n".join(excludes),
                                   encoding="utf-8")

            if rsync.returncode == 0:
                LOGGER.info(f"{backup} backup complete.")
                # take and rotate snapshots now that we're done
                do_rotation(dataset)
                # tell icinga
                passive_report(
                    host="VPN",
                    service="BACKUP",
                    message="Backup completed.",
                    status=0,
                )
            else:
                LOGGER.error(f"{backup} backup failed with:")
                LOGGER.error(rsync.stdout)

        except paramiko.ssh_exception.SSHException:
            LOGGER.error(f"SSHing to {backup} failed")
