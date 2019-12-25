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


def dataset_get_snapshots(dataset):
    """Gets a list of snapshots for a dataset."""
    output = subprocess.check_output(["zfs", "list",
                                      "-t", "snapshot",
                                      "-r", "-d1",
                                      "-H", "-oname",
                                      dataset])
    output = output.decode("utf-8").split("\n")
    output = filter(None, output)
    snaps = list(map(lambda full: full.split("@")[1], output))
    snaps = sorted(snaps)
    return snaps


def dataset_destroy_snapshot(dataset, snap):
    """Destroys a snapshot."""
    subprocess.check_call(["zfs", "destroy", f"{dataset}@{snap}"],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
