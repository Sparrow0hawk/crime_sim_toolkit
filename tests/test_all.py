import os
import json
import unittest
from unittest.mock import patch
import pandas as pd
from crime_sim_toolkit import vis_utils
import crime_sim_toolkit.initialiser as Initialiser

test_dir = os.path.dirname(os.path.abspath(__file__))

class Test(unittest.TestCase):

    def setUp(self):

        self.init = Initialiser.Initialiser()

        self.init_data = self.init.initialise_data(LA_names=['Kirklees','Calderdale','Leeds','Bradford','Wakefield'])

    """ for a given LSOA code this will return the local area code """
    def test_match_LSOA_to_LA(self):

        self.to_match = pd.read_csv(os.path.join(test_dir,'./testing_data/match_LSOA_test.csv'))

        self.assertEqual(vis_utils.match_LSOA_to_LA(self.to_match['LSOA_cd'][0]),self.to_match['LA_cd'][0])

        self.assertEqual(vis_utils.match_LSOA_to_LA(self.to_match['LSOA_cd'][1]),self.to_match['LA_cd'][1])

        self.assertEqual(vis_utils.match_LSOA_to_LA(self.to_match['LSOA_cd'][2]),self.to_match['LA_cd'][2])

    def test_get_Geojson_link(self):

        self.target = 'https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/statistical/eng/lsoa_by_lad/E08000036.json'

        self.assertEqual(vis_utils.get_LA_GeoJson('E08000036'), self.target)

    def test_get_Geojson(self):
        """
        Test to confirm that get_GeoJson function works
        dictionary match between 2 files
        """

        self.data = vis_utils.get_GeoJson(['E09000020'])

        with open(os.path.join(test_dir,'./testing_data/test_1.json')) as datafile , open(os.path.join(test_dir,'./testing_data/test_2.json')) as falsefile:

            self.matchTrue = json.loads(datafile.read())

            self.matchFalse = json.loads(os.path.join(falsefile.read()))

            self.assertEqual(self.data, self.matchTrue)

            self.assertNotEqual(self.data, self.matchFalse)

    @patch('crime_sim_toolkit.vis_utils.get_choropleth', return_value='test')
    def test_map_Geojson(self, input):
        """
        Test to check we can do full data to folium map
        """

        self.data = pd.read_csv(os.path.join(test_dir,'./testing_data/data_to_map.csv'), index_col=False)

        self.test = vis_utils.get_choropleth(data=self.data, inline=False)


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
