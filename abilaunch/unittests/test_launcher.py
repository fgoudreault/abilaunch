import os
import tempfile
import unittest
import shutil
from abilaunch import Launcher


here = os.path.dirname(os.path.abspath(__file__))
Hpseudo = os.path.join(here, "files", "01h.pspgth")
tbase1_1_vars = {"acell": (10, 10, 10),
                 "ntypat": 1,
                 "znucl": 1,
                 "natom": 2,
                 "typat": (1, 1),
                 "xcart": ((-0.7, 0.0, 0.0), (0.7, 0.0, 0.0)),
                 "ecut": 10.0,
                 "kptopt": 0,
                 "nkpt": 1,
                 "nstep": 10,
                 "toldfe": 1.0e-6,
                 "diemac": 2.0,
                 "optforces": 1}


class TestLauncher(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tempdir.cleanup()
        del self.tempdir

    def test_launcher_from_args(self):
        self.launcher = Launcher(self.tempdir.name,
                                 Hpseudo,
                                 input_name="test_launcher.in",
                                 abinit_variables=tbase1_1_vars,
                                 run=True)
        # check that input file is created in good dir
        inputfile = os.path.join(self.tempdir.name, "test_launcher.in")
        outputfile = os.path.join(self.tempdir.name, "test_launcher.out")
        self.assertTrue(os.path.exists(inputfile))
        self.assertTrue(os.path.exists(outputfile))

    def test_launcher_from_args_without_name(self):
        self.launcher = Launcher(self.tempdir.name,
                                 Hpseudo,
                                 abinit_variables=tbase1_1_vars,
                                 run=True)
        # check that input file is created in good dir
        inputfile = os.path.join(self.tempdir.name,
                                 os.path.basename(self.tempdir.name) + ".in")
        outputfile = os.path.join(self.tempdir.name,
                                  os.path.basename(self.tempdir.name) + ".out")
        self.assertTrue(os.path.exists(inputfile))
        self.assertTrue(os.path.exists(outputfile))

    def test_launcher_from_file(self):
        inputpath = os.path.join(here, "files", "tbase1_1.in")
        self.launcher = Launcher.from_files(inputpath,
                                            self.tempdir.name,
                                            Hpseudo,
                                            run=True)
        # check that input file is created in good dir
        inputfile = os.path.join(self.tempdir.name, "tbase1_1.in")
        outputfile = os.path.join(self.tempdir.name, "tbase1_1.out")
        self.assertTrue(os.path.exists(inputfile))
        self.assertTrue(os.path.exists(outputfile))

    def test_raise_when_no_variables(self):
        with self.assertRaises(ValueError):
            self.launcher = Launcher(self.tempdir.name, Hpseudo, run=True)

    def test_raise_pseudos_not_exists(self):
        with self.assertRaises(FileNotFoundError):
            # create new non existant pseudo
            Hpseudo2 = os.path.expanduser("~/pseudo")
            self.launcher = Launcher(self.tempdir.name, Hpseudo2,
                                     abinit_variables=tbase1_1_vars)

    def test_raise_multiple_pseudo_dir(self):
        # temporary copy pseudo in another place
        tempdir2 = tempfile.TemporaryDirectory()
        shutil.copy(Hpseudo, tempdir2.name)
        Hpseudo2 = os.path.join(tempdir2.name, os.path.basename(Hpseudo))
        with self.assertRaises(ValueError):
            self.launcher = Launcher(self.tempdir.name, [Hpseudo, Hpseudo2],
                                     abinit_variables=tbase1_1_vars)
        tempdir2.cleanup()
        del tempdir2
