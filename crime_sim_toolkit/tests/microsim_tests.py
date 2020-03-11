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

        self.loaded_sim = Microsim.Microsimulator()

        self.loaded_sim.load_data(seed_year = 2017,
                                  police_data_dir = os.path.join(test_dir,'testing_data/test_microsim/to_profile_data.csv'),
                                  seed_pop_dir = os.path.join(test_dir,'testing_data/test_microsim/sample_seed_pop.csv'),
                                  spenser_demographic_cols = ['DC1117EW_C_SEX','DC1117EW_C_AGE','DC2101EW_C_ETHPUK11'],
                                  police_demographic_cols = ['sex','age','ethnicity']
                                  )

    def test_load_crime_data(self):
        """
        Test VictimData class
        """

        self.test_sim.load_crime_data(year = 2017.0,
                                      directory = os.path.join(test_dir,'testing_data/test_microsim/sample_vic_data_WY2017.csv')
                                      )

        self.assertTrue(isinstance(self.test_sim.crime_data, pd.DataFrame))

        # test that on passing bad path system exits
        with self.assertRaises(SystemExit) as cm:

            self.test_sim.load_crime_data(year = 2017.0,
                                          directory = os.path.join(test_dir,'testing_data/test_microsim/sample_vic_data_WY2018.csv')
                                         )

        self.assertEqual(cm.exception.code, 0)

    def test_combined_profiles(self):
        """
        Test create_combined_profiles function
        """

        self.loaded_sim.crime_data = self.loaded_sim.create_combined_profiles(dataframe = self.loaded_sim.crime_data,
                                               demographic_cols = ['sex','age','ethnicity'])

        self.assertTrue('victim_profile' in self.loaded_sim.crime_data.columns.tolist())

        self.assertTrue(self.loaded_sim.crime_data.victim_profile[4] == '2-42-2')

        # test error raise if invalid column names passed
        with self.assertRaises(KeyError) as context:

            self.test_sim.create_combined_profiles(dataframe = self.loaded_sim.crime_data,
                                                   demographic_cols = ['name','age','ethnicity'])


    def test_load_seed_pop(self):
        """
        Test for loading the seed population dataset
        and ensuring demographic columns are combined
        """

        self.test_sim.load_seed_pop(os.path.join(test_dir,'testing_data/test_microsim/sample_seed_pop.csv'))

        self.assertTrue(isinstance(self.test_sim.seed_population, pd.DataFrame))

    def test_load_future_pop(self):
        """
        Test function for loading future_population
        """
        self.test_sim.load_future_pop(synthetic_population_dir=os.path.join(test_dir,'testing_data/test_microsim/test_future_pop'),
                                      year=2019)

        self.assertTrue(isinstance(self.test_sim.future_population, pd.DataFrame))

        self.assertEqual(self.test_sim.future_population.shape[0], 2302 * 3)

        with self.assertRaises(ValueError) as context:

            self.test_sim.load_future_pop(synthetic_population_dir=os.path.join(test_dir,'testing_data/test_microsim'),
                                          year=2019)

    def test_get_prob_table(self):
        """
        Test for getting probability table
        """

        self.loaded_sim.generate_probability_table()

        self.assertTrue(isinstance(self.loaded_sim.transition_table))

if __name__ == "__main__":
    unittest.main(verbosity=2)
