import os
import tempfile
import unittest
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
        filespath = os.path.join(here, "files", "tbase1_1.files")
        self.launcher = Launcher.from_files(self.tempdir.name,
                                            inputpath,
                                            filespath, run=True)
        # check that input file is created in good dir
        inputfile = os.path.join(self.tempdir.name, "tbase1_1.in")
        outputfile = os.path.join(self.tempdir.name, "tbase1_1.out")
        self.assertTrue(os.path.exists(inputfile))
        self.assertTrue(os.path.exists(outputfile))

    def test_raise_when_no_variables(self):
        with self.assertRaises(ValueError):
            self.launcher = Launcher(self.tempdir.name, Hpseudo, run=True)

    def test_raise_pseudos_multiple_places(self):
        with self.assertRaises(ValueError):
            # create new non existant pseudo
            Hpseudo2 = os.path.expanduser("~/pseudo")
            self.launcher = Launcher(self.tempdir.name, [Hpseudo, Hpseudo2],
                                     abinit_variables=tbase1_1_vars)
