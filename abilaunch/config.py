import configparser
import os


CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".config", "abilaunch")


class ConfigFileParser:
    def __init__(self):
        D = "DEFAULT"
        self._config = configparser.ConfigParser()
        self._config.read(CONFIG_PATH)
        self.abinit_path = self._config[D]["abinit_path"]
        dpd = "default_pseudos_dir"
        self.default_pseudos_dir = os.path.abspath(self._config[D][dpd])
        self.qsub = self._get_qsub(self._config)

    def _get_qsub(self, config):
        string = self._config["DEFAULT"]["qsub"]
        if string.lower() == "true":
            return True
        return False
