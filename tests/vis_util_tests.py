
import os
import json
import unittest
from unittest.mock import patch
import pandas as pd
from crime_sim_toolkit import vis_utils

test_dir = os.path.dirname(os.path.abspath(__file__))

class Test(unittest.TestCase):

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




if __name__ == "__main__":
    unittest.main(verbosity=2)
