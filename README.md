# AWS Credential Picker (aws-creds)
Makes it easier to use multiple AWS accounts when you don't have SSO available. You can easily save multiple profiles, and then log into them with an simple set of commands.

## Installing

This utility is available in PyPi and can be installed by running:
```
python3 -m pip install aws-creds
```

## Usage

```
MacBook-Pro:aws-creds HammoTime$ aws-creds --help
Usage: aws-creds [OPTIONS] COMMAND [ARGS]...

  aws-creds makes it easier to use multiple AWS accounts when you don't have
  SSO available.  You can easily save multiple profiles, and then log into
  them with an simple set of commands.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  add     Adds a new account profile to '~/.aws/accounts.json'.
  login   Sets the user's AWS credentials to the selected profile.
  logout  Deletes user's current AWS credentials.
  ls      Lists all of the saved profiles.
  rm      Deletes the selected profile.
  status  Prints out information about the credential that is currently in...
  update  Updates the selected profile with the new values.
```

## Commands

The following commands are available within the AWS Credential Picker.

1. ```add```: Add a new credential.
2. ```rm```: Remove a credential.
3. ```ls```: List all the saved credentials.
4. ```login```: Login using a credential.
5. ```logout```: Remove all of the files used by the aws-cli in ~/.aws.
6. ```status```: Print details about the current session (account/user).
7. ```update```: Updates the selected profile with new values.

## Options

The following options are available within the AWS Credential Picker.

1. ```--help```: Show the help screen.
2. ```--version```: Print version details.

## How it Works
The AWS Credential Picker is quite simple in it's design. Instead of storing details in the credentials file - which can prove difficult to use with lots of profiles - we store them in a custom JSON file. When you ```login```, you're actually doing is creating the ```credentials``` and the ```config``` file in ```~/.aws```. When you ```logout```, these files are being deleted.

The reason this was created is that some AWS Utilities and 3rd Party Tools REALLY do not like it if you have multiple profiles and do not treat environment variables correctly. By always having a single credential set, utilities will ALWAYS work.

This script also provides an update on how old your Access Key is and advises you when to rotate them.

## Dependencies

- [boto3](https://pypi.org/project/boto3/)
- [click](https://pypi.org/project/click/)