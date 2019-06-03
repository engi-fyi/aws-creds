import bin.util as util
import bin.cred as cred
import os

def help(subcommands):
    print(util.get_usage_string(subcommands))

def add():
    profile_name = input("What is the name of the profile? ")
    description = input("What is the description of the account? ")
    access_key = input("What is the access key? ")
    secret_key = input("What is the secret key? ")
    region = input("What would you like the default region to be? ")
    output = input("What would you like the default output type to be? ")

    if profile_name and access_key and secret_key and region and output:
        cred_config = {
            "profile": profile_name,
            "description": description,
            "access-key": access_key,
            "secret-key": secret_key,
            "region": region,
            "output": output
        }

        return cred.add(cred_config)
    else:
        print("Sorry, you didn't enter a value for all the options!")

def rm():
    print("Not Yet Implemented!")

def ls():
    print(" ")
    print("Installed AWS Profiles")
    print(" ")
    print(cred.list_all())

def login():
    ls()
    print(" ")
    accounts = cred.get_all()

    try:
        account = int(input("Which account would you like to login to? ")) - 1

        if account < len(accounts):
            cred.login(accounts[account])
            days_old = util.get_access_key_age()

            if days_old == 1:
                time_string = "1 day"
            else:
                time_string = str(days_old) + " days"

            if days_old < 50:
                print('\033[92m' + "Your current access key is " + time_string + " old." + '\033[0m')
            elif days_old < 60:
                print('\033[93m' + "Your current access key is " + time_string + " old." + '\033[0m')
            else:
                print('\033[91m' + "Your current access key is " + time_string + " old." + '\033[0m')
                print('\033[91m' + "Please rotate it immediately (reason: older than 60 days)." '\033[0m')
        else:
            print("Sorry, you haven't picked an option between 1 and " + str(len(accounts)) + ".")
    except:
        print("Sorry, you haven't entered a number.")

def logout():
    cred.logout()
    print("Logged out successfully.")

def update():
    print("Not Yet Implemented!")

def version():
    print("Version: 0.1.0")

def status():
    if os.path.exists(util.get_current_profile_file_name()):
        details = cred.status()

        print("Current Profile: " + util.get_current_profile())
        print("Account Number:  " + details["account"])
        print("Account Aliases: " + str(details["aliases"]))
        print("Username:        " + details["username"])
        print("Access Key:      " + details["access_key"])
    else:
        print("Not logged in.")