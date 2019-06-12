#!/bin/python3
import sys
import click
from creds import cli, cred


@click.group()
@click.version_option()
def main():
    """
        aws-creds makes it easier to use multiple AWS accounts when you don't have SSO available. 
        You can easily save multiple profiles, and then log into them with an simple set of commands.
    """
    pass


@click.group()
def default():
    """
        Used to set the defaults for output type and region.
    """


main.add_command(cli.add)
main.add_command(cli.ls)
main.add_command(cli.rm)
main.add_command(cli.login)
main.add_command(cli.logout)
main.add_command(cli.status)
main.add_command(cli.update)
main.add_command(cli.rotate)
default.add_command(cli.get_defaults)
default.add_command(cli.set_defaults)
main.add_command(default)
cred.Credential.migrate()