Welcome to AbiLaunch
====================

This is a python module to easily launch abinit calculations. This modules
creates an easy interface with abipy.

Installation
------------

Download repository using git::

  $ git clone git@github.com:fgoudreault/abilaunch.git
  $ cd abilaunch

Execute setup script::

  $ pip install .

For a development installation (to modify the code without having to execute
the setup script each time). Use the `-e` flag for the `pip install` command::

  $ pip install -e .

Tests
-----

Just use pytest in main repository for testing (pytest should be installed first)::

  $ pip install pytest
  $ pytest
