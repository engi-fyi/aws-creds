#!/bin/python3
import bin.util as util
import bin.ui as ui
import sys

def main():
    util.init_config()
    subcommands = ["add", "rm", "ls", "login", "logout", "help"]

    if len(sys.argv) >= 2:
        command = sys.argv[1]

        if command in subcommands:
            method = getattr(ui, command)

            if command == "help":
                method(subcommands)
            else:
                method()
        else:
            ui.help(subcommands)
    else:
        ui.help(subcommands)