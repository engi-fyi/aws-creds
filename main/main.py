#!/bin/python3
import ui.creds_ui as creds_ui
import creds.credential as cred
import sys
import click

@click.group()
@click.version_option()
def main():
    """
        aws-creds makes it easier to use multiple AWS accounts when you don't have SSO available. 
        You can easily save multiple profiles, and then log into them with an simple set of commands.
    """
    #util.init_config()

main.add_command(creds_ui.add)
main.add_command(creds_ui.ls)
main.add_command(creds_ui.rm)
main.add_command(creds_ui.login)
main.add_command(creds_ui.logout)
main.add_command(creds_ui.status)
#cred.Credential.migrate()