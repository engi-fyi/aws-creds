import uuid
import os
import json
import datetime

class Credential():
    DEFAULT_CREDENTIAL_DIRECTORY = os.path.expanduser("~/.aws/credential_profiles/")
    OLD_ACCOUNTS_FILE_NAME = os.path.expanduser("~/.aws/accounts.json")
    CONFIG_FILE_NAME = os.path.expanduser("~/.aws/credential_profiles/defaults/defaults.json")
    CURRENT_PROFILE_FILE_NAME = os.path.expanduser("~/.aws/.current_profile")
    AWS_CREDENTIAL_FILE_NAME = os.path.expanduser("~/.aws/credentials")
    AWS_CONFIG_FILE_NAME = os.path.expanduser("~/.aws/config")

    def __init__(self, name, description, access_key, secret_key, region, output, id=str(uuid.uuid4()), create_date=str(datetime.datetime.utcnow().replace(tzinfo=None)), modified_date=None):
        self.id = id
        self.name = name.upper()
        self.description = description
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.output = output
        self.create_date = create_date
        if not modified_date:
            self.modified_date = create_date
        else:
            self.modifed_date = modified_date

    def __lt__(self, other):
        if self.name < other.name:
            return True
        else:
            return False

    def __gt__(self, other):
        if self.name > other.name:
            return True
        else:
            return False

    def to_json(self):
        credential_dictionary = {
            "Id": self.id,
            "Name": self.name,
            "Description": self.description,
            "Credentials": {
                "AccessKey": self.access_key,
                "SecretKey": self.secret_key
            },
            "Options": {
                "Region": self.region,
                "OutputType": self.output
            },
            "CreateDate": self.create_date,
            "ModifiedDate": self.modifed_date
        }

        return json.dumps(credential_dictionary, indent=4)

    @staticmethod
    def from_json(id):
        credential_file_name = Credential.DEFAULT_CREDENTIAL_DIRECTORY + id + "/credential.json"

        if os.path.exists(credential_file_name):
            with open(credential_file_name, "r") as fh:
                existing_credential = json.loads(fh.read())
            
            credential = Credential(
                existing_credential["Name"],
                existing_credential["Description"],
                existing_credential["Credentials"]["AccessKey"],
                existing_credential["Credentials"]["SecretKey"],
                existing_credential["Options"]["Region"],
                existing_credential["Options"]["OutputType"],
                existing_credential["Id"],
                existing_credential["CreateDate"],
                existing_credential["ModifiedDate"]
            )

            return credential
        else:
            raise CredentialNotFoundError(id)

    def save(self):
        credential_file_name = self.get_credential_file_name()
        os.makedirs(self.get_directory(), exist_ok=True)
        self.modifed_date = str(datetime.datetime.utcnow().replace(tzinfo=None))
        serialized_self = self.to_json()

        with open(credential_file_name, "w+") as fh:
            fh.write(serialized_self)

    def login(self):
        credential_file_contents = "[default]" + os.linesep
        credential_file_contents += "aws_access_key_id=" + self.access_key + os.linesep
        credential_file_contents += "aws_secret_access_key=" + self.secret_key

        options_file_contents = "[default]" + os.linesep
        options_file_contents += "region=" + self.region + os.linesep
        options_file_contents += "output=" + self.output

        current_profile_file_contents = self.id

        credential_file = open(Credential.AWS_CREDENTIAL_FILE_NAME, "w+")
        credential_file.write(credential_file_contents)
        credential_file.close()

        current_profile_file = open(Credential.CURRENT_PROFILE_FILE_NAME, "w+")
        current_profile_file.write(current_profile_file_contents)
        current_profile_file.close()

        options_file = open(Credential.AWS_CONFIG_FILE_NAME, "w+")
        options_file.write(options_file_contents)
        options_file.close()

        return True

    def remove(self):
        os.remove(self.get_credential_file_name())
        os.rmdir(self.get_directory())
        self.id = None
        self.name = None
        self.description = None
        self.access_key = None
        self.secret_key = None
        self.region = None
        self.output = None
        self.create_date = None

        return True

    def get_directory(self):
        return Credential.DEFAULT_CREDENTIAL_DIRECTORY + self.id

    def get_credential_file_name(self):
        return self.get_directory() + "/credential.json"

    @staticmethod
    def migrate():
        """
            Run once to migrate file version from < v0.5.0 to new structure.
        """
        if os.path.exists(Credential.OLD_ACCOUNTS_FILE_NAME):
            with open(Credential.OLD_ACCOUNTS_FILE_NAME, "r") as fh:
                old_accounts = json.loads(fh.read())

            os.remove(Credential.OLD_ACCOUNTS_FILE_NAME)

            for old_account in old_accounts:
                new_profile = Credential(
                    old_account["profile"],
                    old_account["description"],
                    old_account["access-key"],
                    old_account["secret-key"],
                    old_account["region"],
                    old_account["output"]
                )
                new_profile.save()

    @staticmethod
    def get_all():
        all_credentials = []
        profiles = os.listdir(Credential.DEFAULT_CREDENTIAL_DIRECTORY)

        for profile in profiles:
            all_credentials.append(Credential.from_json(profile))

        all_credentials.sort()
        return all_credentials

    @staticmethod
    def get_by_access_key(access_key):
        all_credentials = Credential.get_all()

        for credential in all_credentials:
            if credential.access_key == access_key:
                return credential
        
        raise(NoCredentialFoundForAccessKeyError(access_key))
    
    @staticmethod
    def logout():
        if os.path.exists(Credential.CURRENT_PROFILE_FILE_NAME):
            os.remove(Credential.CURRENT_PROFILE_FILE_NAME)

        if os.path.exists(Credential.AWS_CREDENTIAL_FILE_NAME):
            os.remove(Credential.AWS_CREDENTIAL_FILE_NAME)

        if os.path.exists(Credential.AWS_CONFIG_FILE_NAME):
            os.remove(Credential.AWS_CONFIG_FILE_NAME)

        return True
    
    @staticmethod
    def get_current():
        if os.path.exists(Credential.CURRENT_PROFILE_FILE_NAME):
            with open(Credential.CURRENT_PROFILE_FILE_NAME, "r") as fh:
                current_profile_id = fh.read()

            my_credential = Credential.from_json(current_profile_id)
            return my_credential
        else:
            return None

class CredentialNotFoundError(Exception):
    def __init__(self, credential_id):
        self.credential_id = credential_id
        self.message = "The credential was not found in the DEFAULT_CREDENTIAL_DIRECTORY."

class NoCredentialFoundForAccessKeyError(Exception):
    def __init__(self, access_key):
        self.access_key = access_key
        self.message = "Sorry there is no saved profile for the current account. Have you saved it?"