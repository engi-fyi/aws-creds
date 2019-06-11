import bin.util as util
import bin.cred as cred
import os
import click
import pkg_resources

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
    """Adds a new account profile to '~/.aws/accounts.json'."""
    if profile_name and access_key and secret_key and region and output:
        cred_config = {
            "profile": profile_name,
            "description": description,
            "access-key": access_key,
            "secret-key": secret_key,
            "region": region,
            "output": output
        }

        if cred.add(cred_config):
            click.echo("New profile added successfully.")
        else:
            click.echo("Failed to add new profile, please try again.")
    else:
        click.echo("Sorry, you didn't enter a value for all the options!")

@click.command()
def rm():
    """NYI: Not Yet Implemented."""
    click.echo("Not Yet Implemented!")

@click.command()
def ls():
    """Lists all of the profiles currently saved in '~/.aws/accounts.json'."""
    click.echo(" ")
    click.echo("Installed AWS Profiles")
    click.echo(" ")
    click.echo(cred.list_all())

@click.command()
def login():
    """
    Sets the user's AWS credentials to the selected profile. It does
    this by doing the following:

    \b
    1. Retrieves the credential information from '~/.aws/accounts.json'.
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
    click.echo(cred.list_all())
    click.echo(" ")
    accounts = cred.get_all()

    try:
        account = click.prompt("Which account would you like to login to", type=int, prompt_suffix="? ") - 1

        if account < len(accounts):
            cred.login(accounts[account])
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
                util.log_error(str(err), "ui.login()")
                click.echo("Error connecting to your account.")
                click.echo("Please clear any AWS environment variables and try again.")
        else:
            click.echo("Sorry, you haven't picked an option between 1 and " + str(len(accounts)) + ".")
    except click.Abort as interrupt:
        click.echo("Exiting, you haven't been logged in.")
    except Exception as err:
        util.log_error(str(err), "ui.login()")
        click.echo("Sorry, you haven't entered a number.")

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
    cred.logout()
    click.echo("Logged out successfully.")

@click.command()
def update():
    """NYI: Not Yet Implemented."""
    click.echo("Not Yet Implemented!")

@click.command()
def version():
    """Prints out the current version of aws-creds."""
    

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
    if os.path.exists(util.get_current_profile_file_name()):
        details = cred.status()

        click.echo("Current Profile: " + util.get_current_profile())
        click.echo("Account Number:  " + details["account"])
        click.echo("Account Aliases: " + str(details["aliases"]))
        click.echo("Username:        " + details["username"])
        click.echo("Access Key:      " + details["access_key"])
    else:
        click.echo("Not logged in.")