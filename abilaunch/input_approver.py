import warnings


# there is utilities in abipy to validate input files but the only thing they
# do is to call abinit in dry run and check for errors. This approver class
# is more passive as it does not call abinit.


class InputApprover:
    """Class that checks if a set of input variable is
     valid for an abinit calculation. The 'valid' attribute states
     if the input should be good. If it is False, abinit will raise an errored
     if it is launched with these variables.
    """
    def __init__(self, abinit_variables, paral_params=None):
        """
        Parameters
        ----------
        abinit_variables : dict of the abinit variables.
        """
        if not isinstance(abinit_variables, dict):
            raise TypeError("The abinit variables should be a dictionary.")

        ndtset = abinit_variables.get("ndtset", 1)
        self.errors = []
        if ndtset > 1:
            warnings.warn("Input approval is not implemented for multidtset.")
            self.valid = True  # assume true
        else:
            self.valid = self._check_validity(abinit_variables, paral_params)
        if not self.valid:
            print(self.errors)

    def _check_validity(self, abinit_variables, paral_params):
        basics = self._check_basics(abinit_variables)
        paral = self._check_paral_params(abinit_variables, paral_params)
        return basics and paral

    def _check_paral_params(self, abinit_variables, paral_params):
        if paral_params is None:
            # disable check
            return True
        nodes = paral_params["nodes"]
        ppn = paral_params["ppn"]
        mpirun_np = paral_params["mpirun_np"]
        if mpirun_np > ppn:
            self.errors.append("npernode (%i) call uses more proc than avail."
                               " on the nodes (%i)!" % (mpiuseppn, ppn))
            return False

        total_ncpus = nodes * mpirun_np
        npfft = abinit_variables.get("npfft", 1)
        npband = abinit_variables.get("npband", 1)
        npspinor = abinit_variables.get("npspinor", 1)
        # paral_kgb = abinit_variables.get("paral_kgb", None)
        nphf = abinit_variables.get("nphf", 1)
        npkpt = abinit_variables.get("npkpt", 1)
        for name, var in {"nphf": nphf,
                          "npkpt": npkpt,
                          "npspinor": npspinor,
                          "npband": npband,
                          "npfft": npfft}.items():
            if int(var) > total_ncpus:
                self.errors.append("%s is greater than the total"
                                   " number of cpus!" % name)
                return False
        return True

    def _check_basics(self, abivars):
        mandatory = ("ecut", "ntypat", "znucl", "typat", "acell", "rprim")
        keys = list(abivars.keys())
        check1, missings = self._all_in(mandatory, keys)
        tolerances = ("toldfe", "tolwfr", "toldff", "tolrff")
        check2, presents = self._only_one_in(tolerances, keys)
        if not check1:
            self.errors.append("%s should be in the input file!" %
                               str(missings))
            return False
        if not check2:
            self.errors.append("%s are presents in the input file but there"
                               " should be only one from %s." %
                               (str(presents), str(tolerances)))
            return False
        # everything checks out
        return True

    def _only_one_in(self, lst1, lst2):
        # check that there is exactly one item of list 1 in list 2
        presents = []
        result = True
        for item in lst1:
            if item in lst2:
                if len(presents):
                    result = False
                presents.append(item)
        return result, presents

    def _at_least_one_in(self, lst1, lst2):
        # check that at least one item of list 1 is in list 2
        for item in lst1:
            if item in lst2:
                return True
        return False

    def _all_in(self, lst1, lst2):
        # check that all variables in list 1 are in list 2
        missings = []
        result = True
        for item in lst1:
            if item not in lst2:
                result = False
                missings.append(item)
        return result, missings
