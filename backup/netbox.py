"""Interface against Netbox to get hosts to backup."""

from __future__ import annotations

import logging
from typing import Any

import requests

from .config import NETBOX_TOKEN, NETBOX_URL

LOGGER = logging.getLogger(__name__)

LIST_HOSTS_QUERY = """
query listHosts {
  virtual_machine_list {
    name
    tags {
      name
    }
  }
  device_list {
    name
    tags {
      name
    }
  }
}
"""


class NetboxRequestError(Exception):
    """An error occurred in a request to Netbox."""


class NetboxClient:
    def __init__(self, *, graphql_endpoint: str, api_token: str, request_timeout: float = 5) -> None:
        self.graphql_endpoint = graphql_endpoint
        self.api_token = api_token
        self.request_timeout = request_timeout

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Token {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _get_payload(self, query: str, variables: dict[str, str] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "query": query,
        }

        if variables is not None:
            payload["variables"] = variables

        return payload

    def _query(self, query: str, variables: dict[str, str] | None = None) -> dict[str, Any]:  # noqa: FA102
        payload = self._get_payload(query, variables)

        try:
            resp = requests.post(
                self.graphql_endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=self.request_timeout,
            )
        except ConnectionError as e:
            raise NetboxRequestError("Unable to connect to netbox") from e
        except requests.RequestException as e:
            raise NetboxRequestError("Error when requesting data from netbox") from e

        try:
            resp.raise_for_status()
        except requests.RequestException as e:
            # Include GraphQL errors in the exception message.
            try:
                data = resp.json()
            except requests.exceptions.JSONDecodeError:
                message = str(e)
            else:
                errors = data.get("errors")
                message = f"{e}: GraphQL errors: {errors}"
            raise NetboxRequestError(message) from e

        try:
            gql_response = resp.json()
        except requests.exceptions.JSONDecodeError as e:
            raise NetboxRequestError("Netbox returned invalid JSON") from e

        # Check for and raise any GraphQL errors from successful responses.
        if "errors" in gql_response:
            errors = gql_response["errors"]
            raise NetboxRequestError(f"Invalid GraphQL response: {errors}")

        try:
            return gql_response["data"]
        except KeyError as e:
            raise NetboxRequestError(
                "Netbox API response did not contain data.",
            ) from e

    def list_hosts(
        self,
    ) -> list[dict[str, Any]]:
        data = self._query(LIST_HOSTS_QUERY)
        return data["device_list"] + data["virtual_machine_list"]


def get_backup_servers() -> list[str]:
    """Get list of servers to back up from netbox."""
    LOGGER.info("Getting servers to backup from netbox")

    nb = NetboxClient(
        graphql_endpoint=NETBOX_URL,
        api_token=NETBOX_TOKEN,
    )

    to_backup = []

    servers = nb.list_hosts()

    for server in servers:
        if "Backup" in [tag["name"] for tag in server["tags"]]:
            # assume that the server's hostname will be in DNS for now
            to_backup.append(server["name"])
    return to_backup
