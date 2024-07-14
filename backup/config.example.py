"""SOWN Backup configuration."""

from zoneinfo import ZoneInfo

from backup.schedules import Schedules

TIMEZONE = ZoneInfo("Europe/London")

NETBOX_URL = "https://netbox.example.com"
NETBOX_TOKEN = ""
ROTATION_SCHEDULE = {
    Schedules.DAILY: 7,
    Schedules.WEEKLY: 4,
    Schedules.MONTHLY: 24,
    Schedules.YEARLY: 5,
}
ICINGA_URL = "https://icinga.example.com:5665/v1/"
ICINGA_USER = "backups"
ICINGA_PASS = "icingapass"  # noqa: S105
ICINGA_CA = "/var/lib/icinga2/certs/ca.crt"
ICINGA_HOSTNAME = "backup-server"
