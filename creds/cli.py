import click
import sys
import boto3
import datetime
from creds import cred

@click.command()
@click.option("--profile-name", 
              help="Label given to the profile.",
              prompt="Profile Name")
@click.option("--description", 
              help="Full description of the profile.",
              prompt="Description")
@click.option("--access-key", 
              help="AWS Access Key (generated via IAM).",
              prompt="Access Key")
@click.option("--secret-key", 
              help="AWS Secret Key (generated via IAM).",
              hide_input=True,
              prompt="Secret Key")
@click.option("--region", 
              help="Default AWS Region (see https://docs.aws.amazon.com/general/latest/gr/rande.html#ec2_region).",
              prompt="Default Region")
@click.option("--output", 
              help="Default Output Format (valid options: text, json, table)",
              prompt="Output Type")
def add(profile_name, description, access_key, secret_key, region, output):
    """Adds a new credential profile."""
    if profile_name and access_key and secret_key and region and output:
        my_credential = cred.Credential(profile_name, description, access_key, secret_key, region, output)
        my_credential.save()
        click.echo("New profile created successfully.")
    else:
        click.echo("Sorry, you didn't enter a value for all the options!")

@click.command()
def ls():
    """Lists all of the saved profiles."""

    click.echo(" ")
    click.echo("Installed AWS Profiles")
    click.echo(" ")

    my_credentials = cred.Credential.get_all()
    echo_credentials(my_credentials)
    click.echo("There are " + str(len(my_credentials)) + " active profiles.")
    click.echo(" ")

@click.command()
def login():
    """
    Sets the user's AWS credentials to the selected profile. It does
    this by doing the following:

    \b
    1. Retrieves the credential information.
    2. Saves the Access Key an Secret Key under the [default] profile in the
       AWS Credential file under '~/.aws/credentials'.
    3. Saves the Region and Output settings under the [default] profile in
       the AWS Config file under '~/.aws/config'.
    4. Saves the label of the current profile under '~/.aws/profile.cred'.
    5. Adds a history item to '~/.aws/login_history.log'.
    6. Checks the age of the Access Keys and advises the user if they need
       to be rotated.
    
    """
    my_credentials = cred.Credential.get_all()
    echo_credentials(my_credentials)
    selection = click.prompt("Which profile would you like to login to", type=int, prompt_suffix="? ") - 1
    click.echo(" ")
    my_credential = my_credentials[selection]
    my_credential.login()
    click.echo("Successfully logged into '" + my_credential.name + "'.")
    check_credential_age()
    click.echo(" ")

@click.command()
def logout():
    """
    Deletes user's current AWS credentials. It does this by doing 
    the following:

    \b
    1. Deletes the AWS Credential file under '~/.aws/credentials'.
    3. Deletes the AWS Config file under '~/.aws/config'.
    4. Deletes '~/.aws/profile.cred'.
    5. Adds a history item to '~/.aws/login_history.log'.

    N.B. As all the credential/acccount information is actually stored under
    '~/.aws/accounts.json', this has no permanent effect on the user's
    stored credentials.
    
    """
    click.echo(" ")
    cred.Credential.logout()
    click.echo("Logged out successfully.")
    click.echo(" ")

@click.command()
def rm():
    """Deletes the selected profile."""
    try:
        click.echo(" ")
        my_credentials = cred.Credential.get_all()
        echo_credentials(my_credentials)
        selection = click.prompt("Which profile would you like to delete", type=int, prompt_suffix="? ") - 1
        click.echo(" ")
        confirmation = click.prompt("'" + my_credentials[selection].name + "' has been selected for deletion. Are you sure (y/n)", type=str, prompt_suffix="? ").lower()

        if confirmation == "y" or confirmation == "yes":
            my_credentials[selection].remove()
            click.echo("Profile deleted successfully.")
        else:
            click.echo("Deletion not confirmed, not continuing.")
        
        click.echo(" ")
    except click.Abort as interrupt:
        click.echo(" ")
        click.echo(" ")
        click.echo("Exiting, no selection made.")
        click.echo(" ")

@click.command()
def status():
    """
    
    Prints out information about the credential that is currently
    in use. The information it displays to the user is:

    \b
     - Current Profile (Label).
     - Account Number (of the AWS Account/Tenancy).
     - Account Aliases.
     - Username of the IAM User assigned to the Access Key.
     - Access Key.
    
    """

    my_credential = cred.Credential.get_current()

    if my_credential:
        access_key_age = str(get_access_key_age()) + " day(s)."
        details = get_account_details()
        click.echo(" ")
        click.echo("Current Profile: " + my_credential.name)
        click.echo("Account Number:  " + details["account"])
        click.echo("Account Aliases: " + details["aliases"])
        click.echo("Username:        " + details["username"])
        click.echo("Access Key:      " + my_credential.access_key)
        click.echo("Access Key Age:  " + access_key_age)
        click.echo(" ")
    else:
        click.echo(" ")
        click.echo("Not logged in.")
        click.echo(" ")

@click.command()    
def update():
    """Updates the selected profile with the new values."""
    click.echo(" ")
    my_credentials = cred.Credential.get_all()
    echo_credentials(my_credentials)
    selection = click.prompt("Which profile would you like to update", type=int, prompt_suffix="? ") - 1
    my_credential = my_credentials[selection]

    click.echo("If you have no new value, just press enter.")
    click.echo(" ")

    my_credential.name = click.prompt("New Name", default=my_credential.name, show_default=True, type=str)
    my_credential.description = click.prompt("New Description", default=my_credential.description, show_default=True, type=str)
    my_credential.access_key = click.prompt("New Access Key", default=my_credential.access_key, show_default=True, type=str)
    my_credential.secret_key = click.prompt("New Secret Key [*****]", default=my_credential.secret_key, show_default=False, type=str, hide_input=True)
    my_credential.region = click.prompt("New Region", default=my_credential.region, show_default=True, type=str)
    my_credential.output = click.prompt("New Output Type", default=my_credential.output, show_default=True, type=str)

    click.echo(" ")
    my_credential.save()
    click.echo("Profile saved successfully.")
    click.echo(" ")

def get_account_details():
    sts = boto3.client("sts")
    iam = boto3.client("iam")
    session = boto3.Session()
    id = sts.get_caller_identity()
    details = { }
 
    details["account"] = id["Account"]
    details["username"] = id["Arn"].split("/")[1]

    # List account aliases through the pagination interface
    paginator = iam.get_paginator("list_account_aliases")
    for response in paginator.paginate():
        details["aliases"] = response["AccountAliases"][0]

    return details

def echo_credentials(my_credentials):
    for i in range(0, len(my_credentials)):
        my_credential = my_credentials[i]
        option_number = str(i + 1).zfill(3)
        click.echo("[" + option_number + "] " + my_credential.name)
        click.echo("      " + my_credential.description)
        click.echo(" ")

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

def check_credential_age():
    try:
        days_old = get_access_key_age()

        if days_old == 1:
            time_string = "1 day"
        else:
            time_string = str(days_old) + " days"

        if days_old < 50:
            click.echo('\033[92m' + "Your current access key is " + time_string + " old." + '\033[0m')
        elif days_old < 60:
            click.echo('\033[93m' + "Your current access key is " + time_string + " old." + '\033[0m')
        else:
            click.echo('\033[91m' + "Your current access key is " + time_string + " old." + '\033[0m')
            click.echo('\033[91m' + "Please rotate it immediately (reason: older than 60 days)." '\033[0m')
    except Exception as err:
        # util.log_error(str(err), "ui.login()")
        click.echo("Error connecting to your account.")
        click.echo("Please clear any AWS environment variables and try again.")