import json
import os

class DefaultConfiguration():
    CONFIG_FILE_NAME = os.path.expanduser("~/.aws/credential_profiles/defaults/defaults.json")
    DEFAULT_DEFAULTS = {
            "output": "json",
            "region": "us-east-1"
        }

    def __init__(self):
        if not os.path.exists(os.path.dirname(DefaultConfiguration.CONFIG_FILE_NAME)):
            os.makedirs(os.path.dirname(DefaultConfiguration.CONFIG_FILE_NAME))

        if not os.path.exists(DefaultConfiguration.CONFIG_FILE_NAME):
            self.output = DefaultConfiguration.DEFAULT_DEFAULTS["output"]
            self.region = DefaultConfiguration.DEFAULT_DEFAULTS["region"]
            self.save()
        else:
            self.load()

    def save(self):
        defaults = {
            "output": self.output,
            "region": self.region
        }

        with open(DefaultConfiguration.CONFIG_FILE_NAME, "w+") as fh:
            fh.write(json.dumps(defaults, indent=4))

    def load(self):
        with open(DefaultConfiguration.CONFIG_FILE_NAME, "r") as fh:
            defaults = json.loads(fh.read())
            self.output = defaults["output"]
            self.region = defaults["region"]
