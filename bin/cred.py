import json
import bin.util as util
import os

# aws-creds add --profile <profile> --access-key <access_key> --secret-key <secret_key> --region
# aws-creds rm --profile <profile>
# aws-creds ls --info
# aws-creds pick
# aws-creds clear

# cred_config = {
#     "profile": profile_name,
#     "access-key": access_key,
#     "secret-key": secret_key,
#     "region": region,
#     "output": output
# }

def add(cred_config):
    existing_accounts = get_all()

    if cred_config["profile"] in existing_accounts:
        print("Sorry, this profile already exists. Try 'update'.")
        return False
    else:
        existing_accounts.append(cred_config)

    accounts_file = open(util.get_accounts_file_name(), "w+")
    accounts_file.write(json.dumps(existing_accounts, indent=4))
    accounts_file.close()

    return True

def update(cred_config):
    print("NYI: Not Yet Implemented.")
    return False

def remove(arguments):
    print("NYI: Not Yet Implemented.")
    return False

def list_all(all_detail=False):
    formatted_list = ""
    i = 0
    accounts = get_all()

    while(i < len(accounts)):
        formatted_list += "[" + str(i + 1).zfill(3) + "] "
        formatted_list += accounts[i]["profile"].upper() + os.linesep
        formatted_list += "      " + accounts[i]["description"] + os.linesep
        
        if all_detail:
            formatted_list += os.linesep
            formatted_list += "      Region: " + accounts[i]["region"] + os.linesep
            formatted_list += "      Output: " + accounts[i]["output"] + os.linesep

        formatted_list += os.linesep
        i += 1

    formatted_list += "There are " + str(len(accounts)) + " active profiles."

    return formatted_list

def login(cred_config):
    credential_file_contents = "[default]" + os.linesep
    credential_file_contents += "aws_access_key_id=" + cred_config["access-key"] + os.linesep
    credential_file_contents += "aws_secret_access_key=" + cred_config["secret-key"]

    options_file_contents = "[default]" + os.linesep
    options_file_contents += "region=" + cred_config["region"] + os.linesep
    options_file_contents += "output=" + cred_config["output"]

    credential_file = open(util.get_credential_file_name(), "w+")
    credential_file.write(credential_file_contents)
    credential_file.close()

    options_file = open(util.get_config_file_name(), "w+")
    options_file.write(options_file_contents)
    options_file.close()

    util.add_login_history("LOGIN", cred_config["profile"].upper())

    return True

def logout(cred_config):
    print("NYI: Not Yet Implemented.")
    return False

def get_all():
    accounts_file = open(util.get_accounts_file_name(), "r")
    accounts = json.loads(" ".join(accounts_file.readlines()))
    accounts_file.close()
    return accounts

