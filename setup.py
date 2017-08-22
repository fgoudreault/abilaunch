from setuptools import setup
from abilaunch.config import CONFIG_PATH
import configparser
import pip
import os


install_requires = ["abipy", ]

# check if abipy is installed
try:
    abipyexists = True
    import abipy  # noqa
except ImportError:
    abipyexists = False
    print("Abipy is not installed: preparing its installation...")
    # abipy is not installed => install it
    # to install abipy we need to install all those packages manually using pip
    for module in ("numpy", "matplotlib", "netcdf4",
                   "pandas", "pymatgen", "scipy"):
        pip.main(["install", module])

setup(name="abilaunch",
      description="Python package to ease launching calculation using abipy.",
      install_requires=install_requires)

if not abipyexists:
    print("Abipy has been installed and needs the manager.yml"
          " and scheduler.yml files. See Abipy's docs.")


# Setup config file
# create config directory if needed
dirname = os.path.dirname(CONFIG_PATH)
if not os.path.isdir(dirname):
    os.mkdir(dirname)
# create file if it does not exists
if not os.path.isfile(CONFIG_PATH):
    config = configparser.ConfigParser()
    # assume it is in the PATH variable
    config["DEFAULT"] = {"abinit_path": "abinit"}
    # write file
    with open(CONFIG_PATH, "w") as f:
        config.write(f)
    print("A configuration file has been created at %s. Edit it if needed." %
          CONFIG_PATH)
