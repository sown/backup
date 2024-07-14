"""Icinga API interaction code."""

import logging
from typing import Any

import requests

from .config import ICINGA_CA, ICINGA_PASS, ICINGA_URL, ICINGA_USER

LOGGER = logging.getLogger(__name__)


def _post(endpoint: str, data: dict[str, Any], *, accept: str = "application/json") -> requests.Response:
    """Send a post request to the Icinga API."""
    return requests.post(
        ICINGA_URL + endpoint,
        json=data,
        auth=(ICINGA_USER, ICINGA_PASS),
        verify=ICINGA_CA,
        headers={"Accept": accept},
        timeout=5,
    )


def passive_report(host: str, service: str, message: str, status: int) -> None:
    """Report passive check completion."""
    response = _post(
        endpoint="actions/process-check-result",
        data={
            "type": "Service",
            "filter": f'host.name=="{host}" && service.name == "{service}"',
            "plugin_output": message,
            "exit_status": status,
        },
    )
    if response.status_code == 200:
        LOGGER.info(f"Reported passive check {host}/{service} to icinga OK.")
    else:
        LOGGER.error(f"Reporting passive check {host}/{service} to icinga failed:")
        LOGGER.error(response.text)
