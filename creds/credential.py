import uuid
import os
import json

class Credential:
    DEFAULT_CREDENTIAL_DIRECTORY = os.path.expanduser("~/.aws/credential_profiles/")

    def __init(self, id):


    def __init__(self, name, description, access_key, secret_key, region, output):
        create_date = str(datetime.datetime.utcnow().replace(tzinfo=None))

        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.output = output
        self.create_date = create_date
        self.modified_date = create_date

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

        return json.dumps(credential_dictionary)

    def from_json(self, id):
        existing_credential_file_name = DEFAULT_CREDENTIAL_DIRECTORY + id + "/credential.json"

        if os.path.exists(credential_file_name):
            with open(existing_credential_file_name, "r") as fh:
                existing_credential = json.loads(fh.read())
            
            self.id = existing_credential["Id"]
            self.name = existing_credential["Name"]
            self.description = existing_credential["Description"]
            self.access_key = existing_credential["Credentials"]["AccessKey"]
            self.secret_key = existing_credential["Credentials"]["SecretKey"]
            self.region = existing_credential["Options"]["Region"]
            self.output = existing_credential["Options"]["OutputType"]
            self.create_date = existing_credential["CreateDate"]
            self.modified_date = existing_credential["ModifiedDate"]
        else:
            raise CredentialNotFoundError(id)


    def save(self):
        credential_directory = existing_credential_file_name = DEFAULT_CREDENTIAL_DIRECTORY + id
        credential_file_name = credential_dictionary + "/credential.json"
        os.makedirs(credential_directory, exist_ok=True)
        self.modifed_date = str(datetime.datetime.utcnow().replace(tzinfo=None))
        serialized_self = self.to_json()

        with open(credential_file_name, "w+") as fh:
            fh.write(serialized_self)

class CredentialNotFoundError(Exception):
    def __init__(self, credential_id):
        self.credential_id = credential_id
        self.message = "The credential was not found in the DEFAULT_CREDENTIAL_DIRECTORY."