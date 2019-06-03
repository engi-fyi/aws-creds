import os
import json
import datetime

def init_config():
    home_dir = os.path.expanduser("~/.aws")
    accounts_file_name = get_accounts_file_name()
    login_history_file_name = get_login_history_file_name()

    if not os.path.exists(home_dir):
        os.mkdir(home_dir)

    if not os.path.exists(accounts_file_name):
        accounts_file = open(accounts_file_name, "w")
        accounts_file.write("[ ]")
        accounts_file.close()
    
    if not os.path.exists(login_history_file_name):
        add_login_history("INIT","NO_ACCOUNT")

def get_accounts_file_name():
    home_dir = os.path.expanduser("~/.aws")
    return home_dir + "/accounts.json"

def get_login_history_file_name():
    home_dir = os.path.expanduser("~/.aws")
    return home_dir + "/login_history.log"

def get_credential_file_name():
    home_dir = os.path.expanduser("~/.aws")
    return home_dir + "/credentials"

def get_config_file_name():
    home_dir = os.path.expanduser("~/.aws")
    return home_dir + "/config"

def add_login_history(action_type, profile_name):
    login_history_file = open(get_login_history_file_name(), "a")
    login_history_file.write(action_type + "," + profile_name + "," + str(datetime.datetime.now()) + "\n")
    login_history_file.close()

def get_usage_string(arguments, subcommand=None):
    usage_string = ""

    if subcommand:
        command_string = "aws-creds " + subcommand

        arguments_string = command_string
        expanded_arguments_string = command_string

        for argument in arguments:
            arguments_string += " <" + argument + ">"
            expanded_arguments_string += " --" + argument + " " + "<" + argument + ">"
        
        usage_string += "Usage: " + arguments_string + os.linesep
        usage_string += "       " + expanded_arguments_string
    else:
        usage_string = "Usage: aws-creds ["

        for argument in arguments:
            usage_string += argument + "|"
    
        usage_string = usage_string[0:(len(usage_string) - 1)] + "]"

    return usage_string
