"""
testing units of poisson simulator
"""

import os
import json
import unittest
import pandas as pd
import crime_sim_toolkit.initialiser as Initialiser

test_dir = os.path.dirname(os.path.abspath(__file__))

class Test(unittest.TestCase):

    def setUp(self):

        self.init = Initialiser.Initialiser()

    def test_random_date(self):
        """
        test random date generator output is correct format
        TODO: test it generates max and min days in given month
        """

        self.dataTrue = pd.read_csv(os.path.join(test_dir,'./testing_data/random_date1.csv'))

        self.dataFalse = pd.read_csv(os.path.join(test_dir,'./testing_data/random_date2.csv'))

        self.assertTrue(self.init.random_date_allocate(self.dataTrue).columns.contains('Mon'))

        self.assertTrue(self.init.random_date_allocate(self.dataTrue).columns.contains('Day'))

        self.assertTrue(self.init.random_date_allocate(self.dataTrue, Week=True).columns.contains('Week'))

        self.assertFalse(self.init.random_date_allocate(self.dataFalse))


if __name__ == "__main__":
    unittest.main(verbosity=2)
