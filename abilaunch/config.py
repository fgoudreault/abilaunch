import configparser
import os


CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".config", "abilaunch")


class ConfigFileParser:
    def __init__(self):
        self._config = configparser.ConfigParser()
        self._config.read(CONFIG_PATH)
        self.abinit_path = self._config["DEFAULT"]["abinit_path"]
