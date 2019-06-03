# AWS Credential Picker (aws-creds)
Makes it easier to use multiple AWS accounts when you don't have SSO available. You can easily save multiple profiles, and then log into them with an simple set of commands.

## Installing

This utility is available in PyPi and can be installed by running:
```
pip install aws-creds
```

## Usage

```
MacBook-Pro:aws-creds HammoTime$ aws-creds help
Usage: aws-creds [add|rm|ls|login|logout|version|status|help]
```

## Commands

The following commands are available within the AWS Credential Picker.

1. ```add```: Add a new credential.
2. ```rm```: Remove a credential.
3. ```ls```: List all the saved credentials.
4. ```login```: Login using a credential.
5. ```logout```: Remove all of the files used by the aws-cli in ~/.aws.
6. ```version```: Output version details.
7. ```status```: Print details about the current session (account/user).
8. ```help```: Print out **Usage** details.