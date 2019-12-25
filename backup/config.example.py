"""SOWN Backup configuration."""
NETBOX_URL = "https://netbox.example.com"
ROTATION_SCHEDULE = {
    Schedules.DAILY: 7,
    Schedules.WEEKLY: 4,
    Schedules.MONTHLY: 24,
    Schedules.YEARLY: 5,
}
