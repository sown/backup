"""Interface against Netbox to get hosts to backup."""

import logging

import pynetbox  # type: ignore

from .config import NETBOX_TOKEN, NETBOX_URL

LOGGER = logging.getLogger(__name__)


def get_backup_servers() -> list[str]:
    """Get list of servers to back up from netbox."""
    LOGGER.info("Getting servers to backup from netbox")
    nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

    tobackup = []

    devices = list(nb.dcim.devices.all())
    vms = list(nb.virtualization.virtual_machines.all())
    servers = devices + vms

    for server in servers:
        if "Backup" in [tag.name for tag in server.tags]:
            # assume that the server's hostname will be in DNS for now
            tobackup.append(server.name)
    return tobackup
