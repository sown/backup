"""SOWN Backup script."""
import libzfs_core
from pynetbox.api import Api

from .config import NETBOX_URL


def getbackups():
    """Get list of servers to back up from netbox."""
    nb = Api(NETBOX_URL, ssl_verify=False)

    tobackup = []

    devices = nb.dcim.devices.all()
    vms = nb.virtualization.virtual_machines.all()
    servers = devices + vms

    for server in servers:
        if "Backup" in server.tags:
            if not server.primary_ip:
                print("%s has no primary IP" % server.name)
            elif not server.primary_ip.dns_name:
                print("%s has no DNS name for primary IP" % server.name)
            else:
                tobackup.append(server.primary_ip.dns_name)

    return tobackup


def main():
    """Do backups."""
    for backup in getbackups():
        dataset = "data/%s" % backup
        bdataset = bytes(dataset, "ascii")
        if not libzfs_core.lzc_exists(bdataset):
            libzfs_core.lzc_create(bdataset)
            print("created %s" % dataset)
        else:
            print("%s already exists" % dataset)
