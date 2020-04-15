"""
a test file for util functions
"""
import unittest
import numpy as np
import pandas as pd
from crime_sim_toolkit import utils
import pkg_resources


# Could be any dot-separated package/module name or a "Requirement"
resource_package = 'crime_sim_toolkit'

class Test(unittest.TestCase):


    def test_counts_to_reports(self):
        """
        Test the counts_to_reports util function
        """

        self.data = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_oobsplit.csv'))

        self.output = utils.counts_to_reports(self.data)

        # length of new dataframe should equal the sum of all counts of passed data
        self.assertEqual(len(self.output), self.data.Counts.sum())

        # simple check output is actually a dataframe
        self.assertTrue(isinstance(self.output, pd.DataFrame))

        # test unique IDs are produced as expected
        self.assertEqual(self.output.UID[0], 'E010117AN0')

    def test_get_crime_description(self):
        """
        Test that crime description generator works as expected
        """

        # can use the sample crime reports data
        self.data = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/report_2_counts.csv'))

        self.descriptions = utils.populate_offence(self.data)

        self.assertTrue(isinstance(self.descriptions, pd.DataFrame))

        # check anti-social behaviour match is anti-social behaviour and is lowercase
        self.assertEqual(self.descriptions.Crime_description[0], 'anti-social behaviour')

        # check value is contained in list of crime descriptions for Violence and sexual offences
        self.assertTrue(self.descriptions.Crime_description[7] in ['abuse of children through sexual exploitation',
                                                                   'abuse of position of trust of a sexual nature',
                                                                   'assault with injury', 'assault with injury on a constable',
                                                                   'assault with intent to cause serious harm',
                                                                   'assault without injury', 'assault without injury on a constable',
                                                                   'attempted murder', 'causing death by aggravated vehicle taking',
                                                                   'causing death by careless driving under influence of drink or drugs',
                                                                   'causing death by careless or inconsiderate driving',
                                                                   'causing death by driving: unlicensed or disqualified or uninsured drivers',
                                                                   'causing death or serious injury by dangerous driving',
                                                                   'causing or allowing death of child or vulnerable person',
                                                                   'causing sexual activity without consent', 'child abduction',
                                                                   'conspiracy to murder', 'cruelty to children/young persons',
                                                                   'endangering life', 'exposure and voyeurism', 'harassment',
                                                                   'homicide', 'incest or familial sexual offences',
                                                                   'intentional destruction of a viable unborn child', 'kidnapping',
                                                                   'malicious communications', 'modern slavery',
                                                                   'other miscellaneous sexual offences',
                                                                   'procuring illegal abortion',
                                                                   'racially or religiously aggravated assault with injury',
                                                                   'racially or religiously aggravated assault without injury',
                                                                   'racially or religiously aggravated harassment',
                                                                   'rape of a female aged 16 and over',
                                                                   'rape of a female child under 13',
                                                                   'rape of a female child under 16',
                                                                   'rape of a male aged 16 and over', 'rape of a male child under 13',
                                                                   'rape of a male child under 16',
                                                                   'sexual activity etc with a person with a mental disorder',
                                                                   'sexual activity involving a child under 13',
                                                                   'sexual activity involving child under 16',
                                                                   'sexual assault on a female aged 13 and over',
                                                                   'sexual assault on a female child under 13',
                                                                   'sexual assault on a male aged 13 and over',
                                                                   'sexual assault on a male child under 13', 'sexual grooming',
                                                                   'stalking', 'threats to kill',
                                                                   'trafficking for sexual exploitation', 'unnatural sexual offences']
       )

        #self.assertEqual(self.descriptions.columns.tolist(), ['UID','datetime','Crime_description','Crime_type','LSOA_code','Police_force'])

    def test_validate_datetime(self):
        """
        Test that adding zero function works
        """
        self.datatrue = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/report_2_counts.csv'))

        self.datafalse = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/random_date1.csv'))

        self.test1 = utils.validate_datetime(self.datatrue)

        self.test2 = utils.validate_datetime(self.datafalse)

        self.assertTrue(isinstance(self.test1, pd.DataFrame))

        self.assertTrue(np.dtype('datetime64[ns]') in self.test1.dtypes.tolist())

        self.assertFalse(np.dtype('datetime64[ns]') in self.test2.dtypes.tolist())


    def test_sample_perturb(self):
        """
        Test that adding zero function works
        """
        self.data = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_sample_perturb.csv'),
                                    index_col=False)

        self.testpos = utils.sample_perturb(self.data, crime_type='Anti-social behaviour', pct_change=1.1)

        self.testneg = utils.sample_perturb(self.data, crime_type='Violence and sexual offences', pct_change=0.666)

        self.assertEqual(self.testpos.loc[0,'Counts'], 11)

        self.assertEqual(self.testneg.loc[4,'Counts'], 10)

    def test_reverse_offence(self):
        """
        A series of tests for the util.reverse_offence function
        """

        self.data = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/reverse_Crimedescription_test.csv'),
                                index_col=False)

        self.output = utils.reverse_offence(self.data)

        self.assertTrue(isinstance(self.output, pd.DataFrame))

        pd.testing.assert_series_equal(self.output.Crime_type.str.lower(), self.output.Crime_category,
                                       check_names=False)

if __name__ == "__main__":
    unittest.main(verbosity=2)
