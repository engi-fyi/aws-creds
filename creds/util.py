import boto3
import json
import datetime
from creds import cred

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

class TooManyAccessKeysError(Exception):
    def __init__(self, access_keys):
        self.access_keys = access_keys
        self.message = "Sorry, you have too many access keys. I can only rotate when there is a free Access Key slot available."

class NotLoggedInError(Exception):
    def __init__(self):
        self.message = "You're not logged in."

if __name__ == "__main__":
    rotate_access_keys()

