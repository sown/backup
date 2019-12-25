"""Snapshot roation."""
import logging
from datetime import datetime
from typing import List

from .config import ROTATION_SCHEDULE
from .schedules import Schedules
from .zfs import (
    dataset_destroy_snapshot,
    dataset_get_snapshots,
    dataset_snapshot,
)

logger = logging.getLogger(__name__)


def do_rotation(dataset: str) -> None:
    """Create and delete rotating snapshots."""
    snapshot(dataset)
    cleanup(dataset)


def snapshot(dataset: str) -> None:
    """Create snapshots when not existing in the last n days, defined by the Schedule."""
    for schedule in Schedules:
        days = schedule.value
        name = schedule.name.lower()
        dates = get_snapshots(dataset, name)
        if len(dates):
            # we have a snapshot, find the last and how long ago it was
            last = dates[-1]
            diff = (datetime.now() - last).days
            # snapshot if it was as long ago (or longer) than the schedule
            if diff >= days:
                logger.info(f"Snapshotting {dataset}, "
                            f"schedule {name} every {days} days, "
                            f"last snapshot {diff} days ago")
                dataset_snapshot(dataset, get_snap_name(datetime.now(), name))
            else:
                logger.info(f"Skipping snapshot of {dataset}, "
                            f"schedule {name} every {days} days, "
                            f"last snapshot {diff} days ago")
        else:
            # no existing snapshot for this schedule
            # so snapshot now
            logger.info(f"Snapshotting {dataset}, "
                        f"schedule {name} every {days} days, "
                        f"no existing snapshot")
            dataset_snapshot(dataset, get_snap_name(datetime.now(), name))


def cleanup(dataset: str) -> None:
    """Delete old rotating snapshots as defined in ROTATION_SCHEDULE."""
    for schedule, count in ROTATION_SCHEDULE.items():
        name = schedule.name.lower()
        dates = get_snapshots(dataset, name)
        # we only want to keep {count} snapshots, get all the dates before that
        todelete = dates[:-count]
        # and delete them
        for date in todelete:
            snapshot = get_snap_name(date, name)
            logger.info(f"Deleting snapshot {snapshot} for dataset {dataset}")
            dataset_destroy_snapshot(dataset, snapshot)


def get_snapshots(dataset: str, schname: str) -> List[datetime]:
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


def get_snap_name(date: datetime, schname: str) -> str:
    """Get a snapshot name from a date and schedule name."""
    datestr = date.strftime("%Y-%m-%d")
    return f"backup-{schname}-{datestr}"
