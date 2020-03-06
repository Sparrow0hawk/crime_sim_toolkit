import os
import json
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
import folium
import crime_sim_toolkit.microsim as Microsim
import pkg_resources

# specified for directory passing test
test_dir = os.path.dirname(os.path.abspath(__file__))

# Could be any dot-separated package/module name or a "Requirement"
resource_package = 'crime_sim_toolkit'

class Test(unittest.TestCase):

    # leaving in for the future
    #def setUp(self):




    def test_VictimData(self):
        """
        Test VictimData class
        """

        self.VicDat = Microsim.VictimData(year = 2017.0,
                                          directory = os.path.join(test_dir,'testing_data/test_microsim/sample_vic_data_WY2017.csv')
                                         )

        self.VicDat_bad = Microsim.VictimData(year = 2017.0,
                                              directory = os.path.join(test_dir,'testing_data/test_microsim/sample_vic_data_WY2018.csv')
                                             )

        self.test_data = self.VicDat.load_data()

        self.assertTrue(isinstance(self.test_data, pd.DataFrame))

        # test that on passing bad path system exits
        with self.assertRaises(SystemExit) as cm:

            self.VicDat_bad.load_data()

        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
