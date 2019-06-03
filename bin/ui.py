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
        else:
            print("Sorry, you haven't picked an option between 1 and " + str(len(accounts)) + ".")
    except:
        print("Sorry, you haven't entered a number.")


def logout():
    print("Not Yet Implemented!")