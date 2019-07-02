import click
import sys
import boto3
import datetime
from creds import cred, util, defaults


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
              prompt="Default Region",
              default=defaults.DefaultConfiguration().region,
              show_default=True)
@click.option("--output", 
              help="Default Output Format (valid options: text, json, table)",
              prompt="Output Type",
              default=defaults.DefaultConfiguration().output,
              show_default=True)
def add(profile_name, description, access_key, secret_key, region, output):
    """Adds a new credential profile."""
    if profile_name and access_key and secret_key:
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
    click.echo(" ")
    
    try:
        util.check_environment()
        my_credentials = cred.Credential.get_all()
        echo_credentials(my_credentials)
        selection = click.prompt("Which profile would you like to login to", type=int, prompt_suffix="? ") - 1
        click.echo(" ")
        my_credential = my_credentials[selection]
        my_credential.login()
        click.echo("Successfully logged into '" + my_credential.name + "'.")
        check_credential_age()
        click.echo(" ")
    except util.EnvironmentVariableIsSetError as err:
        click.echo("Sorry, there are environment variables set.")
        click.echo(" ")
        
        for v in err.variable_names:
            click.echo(" - " + v)
        
        click.echo(" ")
        click.echo("Please delete the environment variables and try again.")
        click.echo(" ")
    except click.Abort:
        click.echo(" ")
        click.echo(" ")
        click.echo("Exiting, no selection made.")
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
    except click.Abort:
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
        details = util.get_account_details()
        current_role = my_credential.get_current_role()

        # Here so ui doesn't lag when printing details
        if not current_role:
            access_key_age = str(util.get_access_key_age()) + " day(s)."
        
        click.echo(" ")
        click.echo("Current Profile: " + my_credential.name)
        click.echo("Account Number:  " + details["account"])
        click.echo("Account Aliases: " + details["aliases"])
        if current_role:
            click.echo("Assumed Role Arn: " + current_role)
        else:
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
    try:
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
    except click.Abort:
        click.echo(" ")
        click.echo(" ")
        click.echo("Exiting, no selection made.")
        click.echo(" ")


@click.command()
def rotate():
    """
        Automatically rotates your access keys. It is recommended
        you do not unless you only use your access key on a single workstation.
    """
    click.echo(" ")

    if util.logged_in():
        try:
            current_credential = cred.Credential.get_current()
            click.echo("Current Access Key is '" + current_credential.access_key + "'.")
            click.echo("Rotating keys.")
            credential = util.rotate_access_keys()
            click.echo("Rotation successful.")
            click.echo("New Access Key is '" + credential.access_key + "'.")
        except util.NotLoggedInError as err:
            click.echo(err.message)
        except util.TooManyAccessKeysError as err:
            click.echo(err.message)
            click.echo("Access Key 1: " + err.access_keys[0])
            click.echo("Access Key 1: " + err.access_keys[1])
        except cred.NoCredentialFoundForAccessKeyError as err:
            click.echo(err.message + " (" + err.access_key + ")")
    else:
        click.echo("Sorry, you're not logged in.")
    
    click.echo(" ")


@click.command(name="get")
def get_defaults():
    """
    Prints out the current default region and output type for the awscli.
    """
    click.echo(" ")

    default_config = defaults.DefaultConfiguration()
    click.echo("Default Output: " + default_config.output)
    click.echo("Default Region: " + default_config.region)

    click.echo(" ")


@click.command(name="set")
@click.option("--output", default=None, help="The default output type (json, text, or table).")
@click.option("--region", default=None, help="The default AWS region you want to use.")
def set_defaults(output, region):
    """
    Allows you to set the default region and output type for the awscli.
    """
    click.echo(" ")

    default_config = defaults.DefaultConfiguration()

    try:
        if output:
            default_config.output = output
        else:
            default_config.output = click.prompt("New Default Output", default=default_config.output, show_default=True, type=str)
        
        if region:
            default_config.region = region
        else:
            default_config.region = click.prompt("New Default Region", default=default_config.region, show_default=True, type=str)

        default_config.save()
        click.echo("New defaults saved successfully.")

        click.echo(" ")
    except click.Abort:
        click.echo(" ")
        click.echo(" ")
        click.echo("Exiting, no selection made or empty input.")
        click.echo(" ")


@click.command(name="add")
def add_role():
    """
        Adds a role (from another account) that can be assumed using the current
        iam credentials.
    """
    my_credential = cred.Credential.get_current()

    if my_credential:
        click.echo(" ")
        role_arn = click.prompt("Assumed Role Arn?", type=str)
        click.echo(" ")
        my_credential.roles.append(role_arn)
        my_credential.save()
    else:
        click.echo(" ")
        click.echo("Not logged in.")
        click.echo(" ")


@click.command(name="assume")
def assume_role():
    """
        Assumes a role (from another account) using current iam credentials.
    """
    my_credential = cred.Credential.get_current()

    if my_credential:
        if my_credential.get_current_role():
            my_credential.unassume_role()            
            click.echo(" ")
            click.echo("Logged out of current role.")
            click.echo(" ")
        
        details = util.get_account_details()
        click.echo(" ")
        click.echo("Current Profile: " + my_credential.name)
        click.echo("Account Number:  " + details["account"])
        click.echo("Account Aliases: " + details["aliases"])
        click.echo("Username:        " + details["username"])
        click.echo(" ")
        echo_roles(my_credential)
        role_arn_key = click.prompt("Which role would you like to assume", type=int, prompt_suffix="? ") - 1
        my_credential.assume_role(my_credential.roles[role_arn_key])
        click.echo("Role assumed successfully.")
        click.echo(" ")
    else:
        click.echo(" ")
        click.echo("Not logged in.")
        click.echo(" ")


@click.command(name="unassume")
def unassume_role():
    """
        Unassumes a role, giving access to the original account.
    """
    my_credential = cred.Credential.get_current()

    if my_credential:
        my_credential.unassume_role()
        click.echo(" ")
        click.echo("Role unassumed.")
        click.echo(" ")
    else:
        click.echo(" ")
        click.echo("Not logged in.")
        click.echo(" ")

@click.command(name="ls")
def list_roles():
    """
        Lists roles available to assume.
    """
    my_credential = cred.Credential.get_current()

    if my_credential:
        click.echo(" ")
        click.echo("Available Roles")
        click.echo(" ")
        echo_roles(my_credential)
        click.echo("There are " + str(len(my_credential.roles)) + " roles.")
        click.echo(" ")
    else:
        click.echo(" ")
        click.echo("Not logged in.")
        click.echo(" ")


@click.command(name="rm")
def remove_role():
    """
        Removes an assumed role from the credential profile permanently.
    """
    my_credential = cred.Credential.get_current()

    if my_credential:
        if my_credential.get_current_role():
            my_credential.unassume_role()            
            click.echo(" ")
            click.echo("Logged out of current role.")

        click.echo(" ")
        echo_roles(my_credential)
        role_arn_key = click.prompt("Which role would you like to assume", type=int, prompt_suffix="? ") - 1
        removed_role = my_credential.roles.pop(role_arn_key)
        my_credential.save()
        click.echo(" ")
        click.echo("Removed '" + removed_role + "'.")
        click.echo("Role removed successfully.")
        click.echo(" ")
    else:
        click.echo(" ")
        click.echo("Not logged in.")
        click.echo(" ")


def echo_roles(my_credentials):
    for i in range(0, len(my_credentials.roles)):
        role_arn = my_credentials.roles[i]
        option_number = str(i + 1).zfill(3)
        click.echo("[" + option_number + "] " + role_arn)
        click.echo(" ")


def echo_credentials(my_credentials):
    for i in range(0, len(my_credentials)):
        my_credential = my_credentials[i]
        option_number = str(i + 1).zfill(3)
        click.echo("[" + option_number + "] " + my_credential.name)
        click.echo("      " + my_credential.description)
        click.echo(" ")


def check_credential_age():
    try:
        days_old = util.get_access_key_age()

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
        print(err)
        click.echo("Error connecting to your account.")
        click.echo("Please clear any AWS environment variables and try again.")