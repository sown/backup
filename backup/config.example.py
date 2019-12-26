"""SOWN Backup configuration."""
from .schedules import Schedules

NETBOX_URL = "https://netbox.example.com"
ROTATION_SCHEDULE = {
    Schedules.DAILY: 7,
    Schedules.WEEKLY: 4,
    Schedules.MONTHLY: 24,
    Schedules.YEARLY: 5,
}
ICINGA_URL = "https://icinga.example.com:5665/v1/"
ICINGA_USER = "backups"
ICINGA_PASS = "icingagenpass"
ICINGA_CA = "/var/lib/icinga2/certs/ca.crt"
