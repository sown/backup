"""Simple wrapper for zfs shell commands."""
import subprocess
from typing import List

ZFS = "/sbin/zfs"


def dataset_exists(dataset: str) -> bool:
    """Checks if a dataset exists."""
    return subprocess.call([ZFS, "list", dataset],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL) == 0


def dataset_mounted(dataset: str) -> bool:
    """Checks if a dataset is mounted."""
    mounted = subprocess.check_output([ZFS, "get", "-Hovalue", "mounted", dataset])
    return mounted == b"yes\n"


def dataset_mount(dataset: str) -> None:
    """Mounts a dataset."""
    subprocess.check_call([ZFS, "mount", dataset],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)


def dataset_create(dataset: str) -> None:
    """Creates a dataset."""
    subprocess.check_call([ZFS, "create", dataset],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)


def dataset_snapshot(dataset: str, snap: str) -> None:
    """Creates a dataset."""
    subprocess.check_call([ZFS, "snapshot", f"{dataset}@{snap}"],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    return True


def dataset_get_snapshots(dataset: str) -> List[str]:
    """Gets a list of snapshots for a dataset."""
    output = subprocess.check_output([ZFS, "list",
                                      "-t", "snapshot",
                                      "-r", "-d1",
                                      "-H", "-oname",
                                      dataset])
    output = output.decode("utf-8").split("\n")
    output = filter(None, output)
    snaps = list(map(lambda full: full.split("@")[1], output))
    snaps = sorted(snaps)
    return snaps


def dataset_destroy_snapshot(dataset: str, snap: str) -> None:
    """Destroys a snapshot."""
    subprocess.check_call([ZFS, "destroy", f"{dataset}@{snap}"],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
