import boto3
import json
import datetime
import os
from creds import cred


AWS_CLI_ENVIRONMENT_VARIABLES = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
                                 "AWS_SESSION_TOKEN", "AWS_DEFAULT_REGION"
                                 "AWS_DEFAULT_OUTPUT", "AWS_CA_BUNDLE", 
                                 "AWS_SHARED_CREDENTIALS_FILE", "AWS_CONFIG_FILE"]


def logged_in():
    if cred.Credential.get_current():
        return True
    else:
        return False


def get_access_key_age():
    if logged_in():
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
    else:
        raise NotLoggedInError()


def get_account_details():
    if logged_in():
        sts = boto3.client("sts")
        iam = boto3.client("iam")
        id = sts.get_caller_identity()
        details = { }
    
        details["account"] = id["Account"]
        details["username"] = id["Arn"].split("/")[1]

        # List account aliases through the pagination interface
        try:
            paginator = iam.get_paginator("list_account_aliases")
            for response in paginator.paginate():
                details["aliases"] = response["AccountAliases"][0]
        except:
            details["aliases"] = "N/A"

        return details
    else:
        raise NotLoggedInError()


def rotate_access_keys():
    if logged_in():
        iam = boto3.client('iam')
        access_keys = iam.list_access_keys()["AccessKeyMetadata"]
        if len(access_keys) <= 1:
            current_access_key = access_keys[0]["AccessKeyId"]
            account_details = get_account_details()
            new_access_key_details = iam.create_access_key(UserName=account_details["username"])
            credential = cred.Credential.get_by_access_key(current_access_key)
            credential.access_key = new_access_key_details["AccessKey"]["AccessKeyId"]
            credential.secret_key = new_access_key_details["AccessKey"]["SecretAccessKey"]
            credential.save()
            iam.delete_access_key(
                UserName=account_details["username"],
                AccessKeyId=current_access_key
            )
            cred.Credential.logout()
            return credential
        else:
            raise TooManyAccessKeysError([
                access_keys[0]["AccessKeyId"],
                access_keys[1]["AccessKeyId"]
            ])
    else:
        raise NotLoggedInError()


def check_environment():
    current_environment_variables = os.environ.keys()
    disallowed_environment_variables = []

    for cev in current_environment_variables:
        if cev in AWS_CLI_ENVIRONMENT_VARIABLES:
            disallowed_environment_variables.append(cev)
    
    if len(disallowed_environment_variables) > 0:
        raise EnvironmentVariableIsSetError(disallowed_environment_variables)


class EnvironmentVariableIsSetError(Exception):
    def __init__(self, variable_names):
        self.variable_names = variable_names
        self.message = "Sorry, aws-creds doesn't run correctly when there are environment variables set, please remove them."

class TooManyAccessKeysError(Exception):
    def __init__(self, access_keys):
        self.access_keys = access_keys
        self.message = "Sorry, you have too many access keys. I can only rotate when there is a free Access Key slot available."


class NotLoggedInError(Exception):
    def __init__(self):
        self.message = "You're not logged in."