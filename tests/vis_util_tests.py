
import os
import unittest
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
