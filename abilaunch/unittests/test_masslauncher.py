import os
import tempfile
import unittest
from abilaunch import MassLauncher


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


class TestMassLauncher(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tempdir.cleanup()
        del self.tempdir

    def test_masslauncher(self):
        ml = MassLauncher(self.tempdir.name,
                          Hpseudo,
                          ["ecut5", "ecut10"],
                          tbase1_1_vars,
                          [{"ecut": 5}, {"ecut": 10}])
        ecut5path = os.path.join(self.tempdir.name, "ecut5")
        ecut10path = os.path.join(self.tempdir.name, "ecut10")
        for path in (ecut5path, ecut10path):
            self.assertTrue(os.path.exists(path))
        del ml
