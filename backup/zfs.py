"""Simple wrapper for zfs shell commands."""

import subprocess
from collections.abc import Iterable

ZFS = "/sbin/zfs"


def dataset_exists(dataset: str) -> bool:
    """Checks if a dataset exists."""
    return subprocess.call([ZFS, "list", dataset], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def dataset_mounted(dataset: str) -> bool:
    """Checks if a dataset is mounted."""
    mounted = subprocess.check_output([ZFS, "get", "-Hovalue", "mounted", dataset])
    return mounted == b"yes\n"


def dataset_mount(dataset: str) -> None:
    """Mounts a dataset."""
    subprocess.check_call([ZFS, "mount", dataset], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dataset_create(dataset: str) -> None:
    """Creates a dataset."""
    subprocess.check_call([ZFS, "create", dataset], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dataset_snapshot(dataset: str, snap: str) -> None:
    """Creates a dataset."""
    subprocess.check_call([ZFS, "snapshot", f"{dataset}@{snap}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dataset_get_snapshots(dataset: str) -> list[str]:
    """Gets a list of snapshots for a dataset."""
    output_bytes = subprocess.check_output([ZFS, "list", "-t", "snapshot", "-r", "-d1", "-H", "-oname", dataset])
    output = output_bytes.decode("utf-8")
    output_lines: Iterable[str] = output.split("\n")
    output_lines = filter(None, output_lines)

    snaps = [full.split("@")[1] for full in output_lines]
    return sorted(snaps)


def dataset_destroy_snapshot(dataset: str, snap: str) -> None:
    """Destroys a snapshot."""
    subprocess.check_call([ZFS, "destroy", f"{dataset}@{snap}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
