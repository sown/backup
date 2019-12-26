"""Logger setup."""
import logging
import logging.handlers


def logger_setup(quiet: bool) -> None:
    """Setup the logger."""
    logger = logging.getLogger(__package__)
    logger.setLevel(logging.INFO)

    syslog = logging.handlers.SysLogHandler("/dev/log")
    syslog.setLevel(logging.INFO)

    stderr = logging.StreamHandler()
    if quiet:
        stderr.setLevel(logging.WARNING)
    else:
        stderr.setLevel(logging.INFO)
    stderr.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    ))

    logger.addHandler(stderr)
    logger.addHandler(syslog)
