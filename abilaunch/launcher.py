from abipy.htc.launcher import Launcher as AbiLauncher
from abipy.abio.abivars import AbinitInputFile
from .config import ConfigFileParser
from .files_reader import FilesReader
import os


USER_CONFIG = ConfigFileParser()


class Launcher(AbiLauncher):
    """Class that uses an abipy launcher to launch a simple calculation.
    """
    def __init__(self, workdir, pseudos, run=False,
                 input_name=None,
                 overwrite=False, abinit_variables=None,
                 abinit_path=None):
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
        """
        if abinit_variables is None:
            raise ValueError("No abinit variables given...")
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
        self.jobfile.set_stderr(os.path.join(workdir, "stderr"))
        # set input variables
        for varname, varvalue in abinit_variables.items():
            setattr(self, varname, varvalue)

        # write files
        self.make(verbose=1, force=overwrite)
        # run calculation
        if run:
            self.run()

    def _check_pseudos(self, pseudos):
        pseudo_dir = set()
        pseudos_list = []
        if isinstance(pseudos, str):
            pseudos = (pseudos, )
        for pseudo in pseudos:
            pseudo = os.path.expanduser(pseudo)
            pseudos_list.append(os.path.basename(pseudo))
            pseudo_dir.add(os.path.dirname(pseudo))
        if len(pseudo_dir) > 1:
            raise ValueError("Pseudos must all come from the same directory.")
        return pseudo_dir.pop(), pseudos_list

    @classmethod
    def from_files(workdir, input_file_path, files_file_path, **kwargs):
        files = FilesReader(files_file_path)
        inputs = AbinitInputFile(input_file_path)
        return Launcher(workdir, files["pseudos"],
                        input_name=files[".in"],
                        abinit_variables=inputs.datasets[0], **kwargs)
