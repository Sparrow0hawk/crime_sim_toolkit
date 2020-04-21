"""
testing Initialiser class in crime_sim_toolkit
"""

import os
import json
import unittest
import pandas as pd
import crime_sim_toolkit.initialiser as Initialiser
import pkg_resources

# specified for directory passing test
test_dir = os.path.dirname(os.path.abspath(__file__))

# Could be any dot-separated package/module name or a "Requirement"
resource_package = 'crime_sim_toolkit'


test_dir = os.path.dirname(os.path.abspath(__file__))

# Could be any dot-separated package/module name or a "Requirement"
resource_package = 'crime_sim_toolkit'

class Test(unittest.TestCase):

    def setUp(self):

        self.init = Initialiser.Initialiser(LA_names=['Kirklees','Calderdale','Leeds','Bradford','Wakefield'])

        self.init_data = self.init.initialise_data(directory=None)

    def test_random_date(self):
        """
        test random date generator output is correct format
        TODO: test it generates max and min days in given month
        """

        self.dataTrue = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/random_date1.csv'))

        self.dataFalse = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/random_date2.csv'))

        self.assertTrue('datetime' in self.init.random_date_allocate(data=self.dataTrue).columns)

        self.assertFalse('Week' in self.init.random_date_allocate(data=self.dataTrue).columns)

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

        Aggregate set to false
        """

        self.data = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/report_2_counts.csv'))

        test_frame = self.init.reports_to_counts(self.data)

        self.assertEqual(test_frame['datetime'].value_counts().sort_index().index.tolist(),
                         pd.to_datetime(['2017-01-03','2017-01-07','2017-01-08',
                                         '2017-01-09','2017-01-12','2017-01-13',
                                         '2017-01-24','2017-01-26','2017-01-31']).tolist())

        self.assertEqual(test_frame['Counts'].sort_index().tolist(), [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

        self.assertFalse('West Yorkshire' in test_frame.LSOA_code.unique().tolist())

    def test_reports_2_counts_agg(self):
        """
        Test to check the reports to counts converter works

        Includes test of aggregate function

        """
        self.data = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/report_2_counts.csv'))

        test_frame = self.init.reports_to_counts(self.data, aggregate=True)

        self.assertEqual(test_frame['datetime'].value_counts().sort_index().index.tolist(),
                         pd.to_datetime(['2017-01-03','2017-01-07','2017-01-08',
                                         '2017-01-09','2017-01-12','2017-01-13',
                                         '2017-01-24','2017-01-26','2017-01-31']).tolist())

        self.assertEqual(test_frame['Counts'].sort_index().tolist(), [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

        self.assertTrue(test_frame.LSOA_code.unique().tolist()[0], 'West Yorkshire')

    def test_add_zero_counts(self):
        """
        Test that adding zero function works
        """
        self.data = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_counts1.csv'))

        self.test = self.init.add_zero_counts(self.data, timeframe='Day')

        self.assertTrue(isinstance(self.test, pd.DataFrame))

        self.assertEqual(len(self.test[self.test.datetime == '2017-01-07'].LSOA_code.unique()), 1388)

    def test_new_data_load(self):
        """
        Test new data load function

        """

        # pass it the directory to test data
        self.path_good = os.path.abspath(os.path.join(test_dir,'testing_data/test_policedata'))

        self.path_bad = os.path.abspath(os.path.join(test_dir,'testing_data/test_policedata/bad'))

        self.test = self.init.initialise_data(directory=self.path_good)

        self.assertTrue(isinstance(self.init.report_frame, pd.DataFrame))

        # test that on passing bad path system exits
        with self.assertRaises(SystemExit) as cm:

            self.init.initialise_data(directory=self.path_bad)

        self.assertEqual(cm.exception.code, 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
