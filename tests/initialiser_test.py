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

        self.init_data = self.init.initialise_data(LA_names=['Kirklees','Calderdale','Leeds','Bradford','Wakefield'])

    def test_random_date(self):
        """
        test random date generator output is correct format
        TODO: test it generates max and min days in given month
        """

        self.dataTrue = pd.read_csv(os.path.join(test_dir,'./testing_data/random_date1.csv'))

        self.dataFalse = pd.read_csv(os.path.join(test_dir,'./testing_data/random_date2.csv'))

        self.assertTrue(self.init.random_date_allocate(data=self.dataTrue).columns.contains('Mon'))

        self.assertTrue(self.init.random_date_allocate(data=self.dataTrue).columns.contains('Day'))

        self.assertTrue(self.init.random_date_allocate(data=self.dataTrue, Week=True).columns.contains('Week'))

        self.assertFalse(self.init.random_date_allocate(data=self.dataFalse))

    def test_initalise_data(self):

        """
        Test to check initialise data works and loads correct dataframes

        Using example data in data/policedata folder
        """

        col_head = ['Crime ID','Month','Reported by',
                    'Falls within','Longitude','Latitude',
                    'Location','LSOA code','LSOA name',
                    'Crime type','Last outcome category','Context']

        col_head2 = ['LSOA_code','LSOA_name','persons','households']

        self.assertEqual(self.init.report_frame.columns.tolist(), col_head)

        self.assertEqual(self.init.LSOA_hh_counts.columns.tolist(), col_head2)

    def test_reports_2_counts(self):

        """
        Test to check the reports to counts converter works
        """
        self.data = pd.read_csv(os.path.join(test_dir,'./testing_data/report_2_counts.csv'))

        test_frame = self.init.reports_to_counts(self.data)

        pd.testing.assert_series_equal(test_frame['Day'].value_counts().sort_index(), pd.Series([3,2,2,4,1,1], index=[1,4,6,20,7,3], name='Day').sort_index())

        pd.testing.assert_series_equal(test_frame['Counts'].sort_index(), pd.Series([1,1,2,1,1,1,1,1,1,1,1,1,2], index=range(0,13), name='Counts').sort_index())

if __name__ == "__main__":
    unittest.main(verbosity=2)
