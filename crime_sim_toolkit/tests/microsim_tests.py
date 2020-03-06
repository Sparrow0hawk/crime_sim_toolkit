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

    def setUp(self):

        self.test_sim = Microsim.Microsimulator()

        self.loaded_sim = self.test_sim.load_data(year = 2017.0,
                                directory = os.path.join(test_dir,'testing_data/test_microsim/to_profile_data.csv')
                                )

    def test_load_data(self):
        """
        Test VictimData class
        """

        self.test_sim.load_data(year = 2017.0,
                                directory = os.path.join(test_dir,'testing_data/test_microsim/sample_vic_data_WY2017.csv')
                                )

        self.assertTrue(isinstance(self.test_sim.crime_data, pd.DataFrame))

        # test that on passing bad path system exits
        with self.assertRaises(SystemExit) as cm:

            self.test_sim.load_data(year = 2017.0,
                                    directory = os.path.join(test_dir,'testing_data/test_microsim/sample_vic_data_WY2018.csv')
                                    )

        self.assertEqual(cm.exception.code, 0)

    def test_combined_profiles(self):
        """
        Test create_combined_profiles function
        """

        self.test_sim.create_combined_profiles(['sex','age','ethnicity'])

        self.assertTrue('victim_profile' in self.test_sim.crime_data.columns.tolist())

        self.assertTrue(self.test_sim.crime_data.victim_profile[4] == '2-42-2')



if __name__ == "__main__":
    unittest.main(verbosity=2)
