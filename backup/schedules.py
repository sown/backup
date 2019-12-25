"""Backup rotation schedules."""
from enum import Enum


class Schedules(Enum):
    """Enums for schedules, and their duration in days."""

    DAILY = 1
    WEEKLY = 7
    MONTHLY = 30
    YEARLY = 365
