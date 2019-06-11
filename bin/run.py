#!/bin/python3
import bin.util as util
import bin.ui as ui
import sys
import click
import pkg_resources

@click.group()
@click.version_option()
def cli():
    """
        aws-creds makes it easier to use multiple AWS accounts when you don't have SSO available. 
        You can easily save multiple profiles, and then log into them with an simple set of commands.
    """
    util.init_config()

    # subcommands = ["add", "rm", "ls", "login", "logout", "version", "status", "help"]

    # if len(sys.argv) >= 2:
    #     command = sys.argv[1]

    #     if command in subcommands:
    #         method = getattr(ui, command)

    #         if command == "help":
    #             method(subcommands)
    #         else:
    #             method()
    #     else:
    #         ui.help(subcommands)
    # else:
    #     ui.help(subcommands)

cli.add_command(ui.add)
cli.add_command(ui.rm)
cli.add_command(ui.ls)
cli.add_command(ui.login)
cli.add_command(ui.logout)
cli.add_command(ui.status)
cli.add_command(ui.update)