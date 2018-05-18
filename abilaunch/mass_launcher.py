from .launcher import Launcher
from .base import BaseUtility
import logging
import numpy as np
import os


class MassLauncher(BaseUtility):
    def __init__(self,
                 workdir,
                 pseudos,
                 input_names,
                 base_variables,
                 specific_variables,
                 loglevel=logging.INFO,
                 to_link=None, **kwargs):
        """Mass launcher input parameters.

        Parameters
        ----------
        workdir : str
                  Working directory where all launchers will be launched.
        pseudos : list
                  List or list of list (one list for each calculation) of the
                  pseudos used in the calculations.
        input_names : list
                      The list of the names of the calculations. They will
                      be used to name the subdirectory.
        base_variables : dict
                         The list of abinit variables used in
                         each calculations.
        specific_variables : list
                             The list of dictionary of the specific variables
                             for each calculations.
        to_link : str, list, optional
                  A file or a list of file to link to each calculation.
        Other kwargs (like run and overwrite) are passed directly to each
        sublauncher.
        """
        super().__init__(loglevel)
        length = self._list_check(input_names, specific_variables)
        pseudos, to_link = self._sanitize_list_format(length, pseudos, to_link)
        kwargs = self._sanitize_dict_format(length, **kwargs)
        workdir = os.path.abspath(workdir)
        if not os.path.exists(workdir):
            os.mkdir(workdir)

        self._launchers = self._launch(workdir, pseudos, input_names,
                                       base_variables,
                                       specific_variables, to_link, loglevel, **kwargs)

    def _launch(self, workdir, pseudos, input_names, base_variables,
                specific_variables, to_link, loglevel, **kwargs):
        launchers = []
        for i, (input_name, pseudo,
                specifics, to_link_here) in enumerate(zip(input_names,
                                                          pseudos,
                                                          specific_variables,
                                                          to_link)):
            if input_name.endswith(".in"):
                input_name = input_name[:-3]
            path = os.path.join(workdir, input_name)
            abinit_vars = base_variables.copy()
            abinit_vars.update(specifics)
            kwargs_here = {k: v[i] for k, v in kwargs.items()}
            l = Launcher(path, pseudo,
                         input_name=input_name,
                         abinit_variables=abinit_vars,
                         to_link=to_link_here,
                         loglevel=loglevel,
                         **kwargs_here)
            launchers.append(l)
        return launchers

    def _sanitize_dict_format(self, length, **kwargs):
        toreturn = {}
        for key, value in kwargs.items():
            if not self._is_list(value):
                value = [value] * length
            toreturn[key] = value
        return toreturn

    def _sanitize_list_format(self, length, *args):
        # check that all args are either a string, a list of string
        # or a list of list of strings
        # length is the length of the returned list
        toreturn = []
        for arg in args:
            if not self._is_list(arg):
                toreturn.append([arg] * length)
                continue
            # here, it should be a list type and so it is ok
            toreturn.append(arg)
        return toreturn

    def _list_check(self, *args):
        # check that all args are lists or lists-like and that each has
        # the same length
        length = None
        for l in args:
            if not self._is_list(l):
                raise ValueError("%s is not a list!" % str(l))
            if length is None:
                length = len(l)
            if len(l) != length:
                raise ValueError("Not all args have the same length!")
        return length

    def _is_list(self, a_list):
        types = (list, tuple, np.ndarray)
        for typ in types:
            if isinstance(a_list, typ):
                return True
        return False
