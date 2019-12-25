"""Snapshot roation."""
import logging
from datetime import datetime

from .config import ROTATION_SCHEDULE
from .schedules import Schedules
from .zfs import (
    dataset_destroy_snapshot,
    dataset_get_snapshots,
    dataset_snapshot,
)

logger = logging.getLogger(__name__)


def do_rotation(dataset):
    """Create and delete rotating snapshots."""
    snapshot(dataset)
    cleanup(dataset)


def snapshot(dataset):
    """Create rotating snapshots as needed."""
    for schedule in Schedules:
        days = schedule.value
        name = schedule.name.lower()
        dates = get_snapshots(dataset, name)
        if len(dates):
            last = dates[-1]
            diff = (datetime.now() - last).days
            if diff >= days:
                logger.info(f"Snapshoting {dataset}, "
                            f"schedule {name} every {days} days, "
                            f"last snapshot {diff} days ago")
                dataset_snapshot(dataset, get_snap_name(datetime.now(), name))
            else:
                logger.info(f"Skipping snapshot of {dataset}, "
                            f"schedule {name} every {days} days, "
                            f"last snapshot {diff} days ago")
        else:
            logger.info(f"Snapshoting {dataset}, "
                        f"schedule {name} every {days} days, "
                        f"no existing snapshot")
            dataset_snapshot(dataset, get_snap_name(datetime.now(), name))


def cleanup(dataset):
    """Delete old rotating snapshots as defined in ROTATION_SCHEDULE."""
    for schedule, count in ROTATION_SCHEDULE.items():
        name = schedule.name.lower()
        dates = get_snapshots(dataset, name)
        todelete = dates[:-count]
        for date in todelete:
            snapshot = get_snap_name(date, name)
            logger.info(f"Deleting snapshot {snapshot} for dataset {dataset}")
            dataset_destroy_snapshot(dataset, snapshot)


def get_snapshots(dataset, schname):
    """Gets snapshot dates (sorted) for a schedule name."""
    snaps = dataset_get_snapshots(dataset)
    dates = []
    for snap in snaps:
        try:
            dates.append(datetime.strptime(snap, f"backup-{schname}-%Y-%m-%d"))
        except ValueError:
            # snapshot didn't match our scheme, ignore
            pass
    return dates


def get_snap_name(date, schname):
    """Get a snapshot name from a date and schedule name."""
    datestr = date.strftime("%Y-%m-%d")
    return f"backup-{schname}-{datestr}"
