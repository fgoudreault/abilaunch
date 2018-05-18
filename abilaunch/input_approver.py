from .base import BaseUtility
import logging


# there is utilities in abipy to validate input files but the only thing they
# do is to call abinit in dry run and check for errors. This approver class
# is more passive as it does not call abinit.


class InputApprover(BaseUtility):
    """Class that checks if a set of input variable is
     valid for an abinit calculation. The 'valid' attribute states
     if the input should be good. If it is False, abinit will raise an errored
     if it is launched with these variables.
    """
    _loggername = "InputApprover"

    def __init__(self, abinit_variables, paral_params=None,
                 loglevel=logging.INFO):
        """
        Parameters
        ----------
        abinit_variables : dict of the abinit variables.
        """
        super().__init__(loglevel=loglevel)
        if not isinstance(abinit_variables, dict):
            raise TypeError("The abinit variables should be a dictionary.")

        ndtset = abinit_variables.get("ndtset", 1)
        self.errors = []
        if ndtset > 1:
            self._logger.warning("Input approval is not implemented"
                                 " for multidtset.")
            self.valid = True  # assume true
        else:
            self.valid = self._check_validity(abinit_variables, paral_params)
        if not self.valid:
            print(self.errors)

    def _check_validity(self, abinit_variables, paral_params):
        nscf_ok = self._check_nscf_ok(abinit_variables)
        basics = self._check_basics(abinit_variables)
        paral = self._check_paral_params(abinit_variables, paral_params)
        return basics and paral and nscf_ok

    def _check_nscf_ok(self, abinit_variables):
        iscf = abinit_variables.get("iscf", 0)
        if iscf < 0 and iscf != -3:
            # iscf < 0 and iscf != -3 => nscf calculation
            # check that tolwfr > 0
            tolwfr = abinit_variables.get("tolwfr", 0.0)
            if tolwfr <= 0.0:
                self.errors.append("for iscf < 0 and != -3, tolwfr"
                                   "  must be > 0.")
                return False
        return True

    def _check_paral_params(self, abinit_variables, paral_params):
        if paral_params is None:
            # disable check
            return True
        nodes = paral_params["nodes"]
        ppn = paral_params["ppn"]
        mpirun_np = paral_params["mpirun_np"]
        if mpirun_np is None:
            # No parallelization
            return True
        if mpirun_np > ppn:
            self.errors.append(f"npernode {mpirun_np} call uses"
                               f" more proc than available"
                               f" on the nodes ({ppn})!")
            return False
        if isinstance(nodes, str):
            if ":" in nodes:
                # nodes = 3:m48G  for example
                nodes = int(nodes.split(":")[0])
            else:
                nodes = int(nodes)
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
        mandatory = ("ecut", "ntypat", "znucl", "typat", "acell")
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
