"""
TODO: refactor all tests into class distinct scripts
"""
import os
import json
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from crime_sim_toolkit import utils
import pkg_resources

# specified for directory passing test
test_dir = os.path.dirname(os.path.abspath(__file__))

# Could be any dot-separated package/module name or a "Requirement"
resource_package = 'crime_sim_toolkit'

class Test(unittest.TestCase):

    def test_days_in_month_dict(self):
        """
        Test that days_in_month_dict util function
        """

        self.data = pd.DataFrame.from_dict({'Month' : ['2017-01', '2017-02','2017-03'],
                                            'Extra' : ['foo', 'bar','stick']})

        days_dict = utils.days_in_month_dict(self.data)

        self.assertTrue(isinstance(days_dict, dict))

        self.assertEqual(days_dict['2017-01'], 31)


if __name__ == "__main__":
    unittest.main(verbosity=2)
