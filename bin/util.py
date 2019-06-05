import os
import json
import datetime
import boto3

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

def get_current_profile_file_name():
    home_dir = os.path.expanduser("~/.aws")
    return home_dir + "/profile.cred"

def get_error_log_file_name():
    home_dir = os.path.expanduser("~/.aws")
    return home_dir + "/error.log"

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

def get_current_profile():
    current_profile_file = open(get_current_profile_file_name(), "r")
    current_profile = current_profile_file.read()
    current_profile_file.close()
    return current_profile

def get_access_key_age():
    session = boto3.Session()
    credentials = session.get_credentials()
    access_key_id = credentials.access_key
    iam = boto3.client('iam')
    access_keys = iam.list_access_keys()
    days_old = 0

    for access_key_metadata in access_keys["AccessKeyMetadata"]:
        if access_key_metadata["AccessKeyId"] == access_key_id:
            create_date = access_key_metadata["CreateDate"].replace(tzinfo=None)
            current_time = datetime.datetime.utcnow().replace(tzinfo=None)
            time_string = str(current_time - create_date).split(",")[0]
            try:
                days_old = int(time_string.split(" ")[0])
            except:
                days_old = 0

    return days_old

def log_error(error_text, function_name):
    if os.path.exists(get_error_log_file_name()):
        error_file = open(get_error_log_file_name(), "r")
        existing_errors = json.loads(error_file.read())
        error_file.close()
    else:
        existing_errors = []
    
    error = {
        "datetime": str(datetime.datetime.utcnow().replace(tzinfo=None)),
        "error": error_text,
        "occured_in": function_name
    }

    existing_errors.insert(0, error)
    
    if len(existing_errors) > 100:
        existing_errors.pop()

    error_file = open(get_error_log_file_name(), "w+")
    error_file.write(json.dumps(existing_errors))
    error_file.close()