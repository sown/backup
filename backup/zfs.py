"""Simple wrapper for zfs shell commands."""
import subprocess


def dataset_exists(dataset):
    """Checks if a dataset exists."""
    return subprocess.call(["zfs", "list", dataset],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL) == 0


def dataset_mounted(dataset):
    """Checks if a dataset is mounted."""
    mounted = subprocess.check_output(["zfs", "get", "-Hovalue", "mounted", dataset])
    return mounted == b"yes\n"


def dataset_mount(dataset):
    """Mounts a dataset."""
    subprocess.check_call(["zfs", "mount", dataset],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    return True


def dataset_create(dataset):
    """Creates a dataset."""
    subprocess.check_call(["zfs", "create", dataset],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    return True


def dataset_snapshot(dataset, snap):
    """Creates a dataset."""
    subprocess.check_call(["zfs", "snapshot", f"{dataset}@{snap}"],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    return True
