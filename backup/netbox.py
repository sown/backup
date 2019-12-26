"""Interface against Netbox to get hosts to backup."""
import logging
from typing import List

from pynetbox.api import Api

from .config import NETBOX_URL

LOGGER = logging.getLogger(__name__)


def get_backup_servers() -> List[str]:
    """Get list of servers to back up from netbox."""
    LOGGER.info(f"Getting servers to backup from netbox")
    nb = Api(NETBOX_URL, ssl_verify=False)

    tobackup = []

    devices = nb.dcim.devices.all()
    vms = nb.virtualization.virtual_machines.all()
    servers = devices + vms

    for server in servers:
        if "Backup" in server.tags:
            # assume that the server's hostname will be in DNS for now
            tobackup.append(server.name.lower())
    return tobackup
