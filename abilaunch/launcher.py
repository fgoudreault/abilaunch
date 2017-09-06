from abipy.htc.launcher import Launcher as AbiLauncher
from abipy.abio.abivars import AbinitInputFile
from .config import ConfigFileParser
from .input_approver import InputApprover
from timeit import default_timer as timer
import os
import shutil
import tempfile
import traceback
import warnings


USER_CONFIG = ConfigFileParser()


class Launcher(AbiLauncher):
    """Class that uses an abipy launcher to launch a simple calculation.
    """
    def __init__(self, workdir, pseudos, run=False,
                 input_name=None,
                 overwrite=False,
                 abinit_variables=None,
                 abinit_path=None,
                 to_link=None,
                 **kwargs):
        """Launcher class init method.

        Parameters
        ----------
        workdir : str
                  Path (can be relative to home) to working directory.
        pseudos : list, str
                  The list of path to the pseudos. If only one pseudo, this do
                  not need to be a list.
        run : bool, optional
              If True, the Launcher will launch the
              calculation on instantiation.
        input_name : str, optional
                     Base name for the files.
        overwrite : bool, optional
                    If True, if input files already exists
                    they will be overwritten.
        abinit_variables : dict
                           A dictionary containing all abinit variables
                           used in the input file.
                           Each key represents the name of a variable.
        to_link : list, str
                  A list of input files to link.
        kwargs : other attributes given to the jobfile.
        """
        if abinit_variables is None:
            raise ValueError("No abinit variables given...")
        self._approve_input(abinit_variables, **kwargs)

        workdir = os.path.abspath(os.path.expanduser(workdir))
        # create calculation
        if input_name is not None:
            if input_name.endswith(".in"):
                input_name = input_name[:-3]
        else:
            # input file name is the same as working directory
            input_name = os.path.basename(workdir)
        calcname = os.path.join(workdir, input_name)
        super().__init__(calcname)

        # set executable if custom one is used
        if abinit_path is None:
            abinit_path = USER_CONFIG.abinit_path
        self.set_executable(abinit_path)

        # set pseudos
        pseudo_dir, pseudos = self._check_pseudos(pseudos)
        self.set_pseudodir(pseudo_dir)
        self.set_pseudos(pseudos)

        # set stderr to same directory of input file
        stderrname = os.path.basename(self.jobfile.stderr)
        self.jobfile.set_stderr(os.path.join(workdir, stderrname))
        # samething for logfile
        logname = os.path.basename(self.jobfile.log)
        self.jobfile.set_log(os.path.join(workdir, logname))
        # set input variables
        for varname, varvalue in abinit_variables.items():
            setattr(self, varname, varvalue)

        # link input files
        self._process_to_link(to_link)

        kwargs = self._process_jobfile(workdir, **kwargs)
        if kwargs:
            raise ValueError("These variables were not used: %s" % str(kwargs))
        # write files
        self.make(verbose=1, force=overwrite)
        # run calculation
        if run:
            self.run()

    def run(self, submit=None):
        if (USER_CONFIG.qsub and submit is None) or submit:
            self.submit(verbose=1)
        else:
            start = timer()
            super().run(verbose=1)
            end = timer()
            print("Computation finished in %ss." % str(end - start))

    def _process_jobfile(self, workdir, **kwargs):
        # Add MPI lines to jobfile if needed
        # use setter
        jobname = kwargs.pop("jobname", None)
        if jobname is not None:
            if len(jobname) > 16:
                warnings.warn("jobname: %s is longer than 16 char."
                              " It will be crop." % jobname)
        if jobname is None and USER_CONFIG.qsub:
            # automaticaly choose workdir name
            jobname = os.path.basename(workdir)
            if len(jobname) > 16:
                jobname = jobname[:15]
            warnings.warn("No jobname given. Took %s as jobname." % jobname)
        for name, attr in {"jobname": jobname,
                           "nodes": kwargs.pop("nodes", None),
                           "ppn": kwargs.pop("ppn", None),
                           "runtime": kwargs.pop("runtime", None),
                           "memory": kwargs.pop("memory", None),
                           }.items():
            if attr is not None:
                func = "self.set_" + name
                eval(func)(attr)
        # use attribute setting directly
        for name, lines in {"lines_before": kwargs.pop("lines_before", None),
                            "lines_after": kwargs.pop("lines_after", None),
                            "other_lines": kwargs.pop("other_lines", None),
                            "modules": kwargs.pop("modules", None),
                            "mpirun": kwargs.pop("mpirun", None)}.items():
            if lines is not None:
                setattr(self.jobfile, name, lines)
        # return rest of kwargs
        return kwargs

    def _process_to_link(self, to_link):
        if to_link is None:
            return
        if isinstance(to_link, str):
            to_link = (to_link, )
        for filename in to_link:
            path = os.path.abspath(os.path.expanduser(filename))
            if not os.path.exists(path):
                raise FileNotFoundError("File to link not found: %s" %
                                        filename)
            self.link_idat(path)

    def _check_pseudos(self, pseudos):
        pseudo_dir = set()
        pseudos_list = []
        if isinstance(pseudos, str):
            pseudos = (pseudos, )
        for pseudo in pseudos:
            pseudo = self._check_pseudo_exists(pseudo)
            pseudos_list.append(os.path.basename(pseudo))
            pseudo_dir.add(os.path.dirname(pseudo))
        if len(pseudo_dir) > 1:
            raise ValueError("Pseudos must all come from the same directory.")
        return pseudo_dir.pop(), pseudos_list

    def _check_pseudo_exists(self, pseudo):
        # check is a pseudo exists if not, try to locate it under
        # the default pseudo dir
        # once it is found, return the full path to it
        error = FileNotFoundError("Could not locate pseudo %s" % pseudo)
        pseudo = os.path.expanduser(pseudo)  # get rid of "~"
        if os.path.exists(pseudo):
            return os.path.abspath(pseudo)
        if USER_CONFIG.default_pseudos_dir == "none":  # pragma: nocover
            raise error
        indefault = os.path.join(USER_CONFIG.default_pseudos_dir, pseudo)
        if os.path.exists(indefault):  # pragma: nocover
            return os.path.abspath(indefault)
        # if we are here, raise same error
        raise error

    @classmethod
    def from_files(cls, input_file_path, *args, **kwargs):
        inputs = AbinitInputFile(input_file_path)
        input_name = kwargs.pop("input_name", None)
        if input_name is None:
            input_name = os.path.basename(input_file_path)
        return Launcher(*args,
                        abinit_variables=inputs.datasets[0],
                        input_name=input_name,
                        **kwargs)

    @classmethod
    def from_inplace_input(cls, inputfilename, *args, **kwargs):
        # use inplace inputfile
        # to make it work with abipy, we need to erase it temporarily such that
        # abipy is able to create the rest of files
        tempdir = tempfile.TemporaryDirectory()
        filename = os.path.basename(inputfilename)
        shutil.copy2(inputfilename, os.path.join(tempdir.name, filename))
        os.remove(inputfilename)
        newpath = os.path.join(tempdir.name, filename)
        run = kwargs.pop("run", False)
        try:
            success = True
            l = Launcher.from_files(newpath, *args, run=False, **kwargs)
        except Exception as e:  # pragma: nocover
            success = False
            warnings.warn("An error occured. Full Traceback:")
            tb = traceback.format_exc()
            print(tb)
        else:
            # delete input file created by abipy
            os.remove(inputfilename)
        finally:
            # once all is created, restore input file
            shutil.copy2(newpath, os.path.abspath(inputfilename))
            # cleanup temporary dir
            tempdir.cleanup()
            del tempdir
            if success:
                if run:
                    # run abinit if specified
                    l.run()
                return l

    def _get_mpirun_np(self, **kwargs):
        mpirun = kwargs.get("mpirun", None)
        if mpirun is None:
            return None
        # mpirun == 'mpirun -np 12'
        # mpirun == 'mpiexec -npernode 12'
        split = mpirun.split()
        try:
            i = int(split[-1])
        except ValueError:
            return None
        else:
            return i

    def _approve_input(self, abinit_variables, **kwargs):
        # check the input variables
        paral_vars = {"nodes": kwargs.get("nodes", None),
                      "ppn": kwargs.get("ppn", None),
                      "mpirun_np": self._get_mpirun_np(**kwargs)}
        # if all paralvars are None, use None instead
        useparal = None
        for k, v in paral_vars.items():
            if v is not None:
                useparal = paral_vars
                break
        approver = InputApprover(abinit_variables, useparal)
        if not approver.valid:
            raise ValueError("Input file errors: %s" % str(approver.errors))
