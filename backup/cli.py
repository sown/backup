"""CLI."""
import logging
import random

import click

from .backup import backup_server
from .logconfig import logger_setup
from .netbox import get_backup_servers

LOGGER = logging.getLogger(__name__)


@click.command()
@click.argument("server")
@click.option("-f", "--force", help="Back up server not in netbox",
              is_flag=True, default=False)
@click.option("-q", "--quiet", help="Only output errors",
              is_flag=True, default=False)
def cli(server, force, quiet) -> None:
    """Backup SERVER.

    If SERVER is 'all', all hosts with the Netbox tag 'Backup'
    will be backed up.
    """
    logger_setup(quiet)

    servers = []

    if not force:
        servers = get_backup_servers()

    if server == "all":
        random.shuffle(servers)
        for server in servers:
            backup_server(server)
    else:
        if force or server in servers:
            backup_server(server)
        else:
            click.echo(f"{server} wasn't found in netbox. "
                       "Run with --force to back up anyway.")
