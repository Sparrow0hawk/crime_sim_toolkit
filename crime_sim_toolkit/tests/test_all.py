import os
import json
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
import folium
from crime_sim_toolkit import vis_utils, utils
import crime_sim_toolkit.initialiser as Initialiser
import crime_sim_toolkit.poisson_sim as Poisson_sim
import pkg_resources

# specified for directory passing test
test_dir = os.path.dirname(os.path.abspath(__file__))

# Could be any dot-separated package/module name or a "Requirement"
resource_package = 'crime_sim_toolkit'

class Test(unittest.TestCase):

    def setUp(self):

        self.init = Initialiser.Initialiser(LA_names=['Kirklees','Calderdale','Leeds','Bradford','Wakefield'])

        self.init_data = self.init.initialise_data(directory=None)

    @classmethod
    def setUpClass(cls):
        super(Test, cls).setUpClass()

        cls.poisson = Poisson_sim.Poisson_sim(LA_names=['Kirklees','Calderdale','Leeds','Bradford','Wakefield'],
                                              directory=None,
                                              timeframe='Week')

        cls.poisson_day = Poisson_sim.Poisson_sim(LA_names=['Kirklees','Calderdale','Leeds','Bradford','Wakefield'],
                                                  directory=None,
                                                  timeframe='Day')

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

    def test_match_LSOA_to_LA(self):
        """
        test for a given LSOA code this will return the local area code
        """

        self.to_match = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/match_LSOA_test.csv'))

        self.assertEqual(vis_utils.match_LSOA_to_LA(self.to_match['LSOA_cd'][0]),self.to_match['LA_cd'][0])

        self.assertEqual(vis_utils.match_LSOA_to_LA(self.to_match['LSOA_cd'][1]),self.to_match['LA_cd'][1])

        self.assertEqual(vis_utils.match_LSOA_to_LA(self.to_match['LSOA_cd'][2]),self.to_match['LA_cd'][2])

    def test_get_Geojson_link(self):
        """
        test that link retrieved is correct
        """

        self.target = 'https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/statistical/eng/lsoa_by_lad/E08000036.json'

        self.assertEqual(vis_utils.get_LA_GeoJson('E08000036'), self.target)

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

    def test_get_Geojson(self):
        """
        Test to confirm that get_GeoJson function works
        dictionary match between 2 files
        """

        self.data = vis_utils.get_GeoJson(['E09000020'])

        with open(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_1.json')) as datafile , open(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_2.json')) as falsefile:

            self.matchTrue = json.loads(datafile.read())

            self.matchFalse = json.loads(os.path.join(falsefile.read()))

            self.assertEqual(self.data, self.matchTrue)

            self.assertNotEqual(self.data, self.matchFalse)

    @patch('builtins.input', return_value='test')
    def test_map_Geojson(self, input):
        """
        Test to check we can take a dataframe and build a folium map
        """

        self.data = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/data_to_map.csv'), index_col=False)

        self.test = vis_utils.get_choropleth(data=self.data, inline=False)

        self.assertTrue(isinstance(self.test, folium.Map))


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

    def test_oob(self):
        """
        Test for checking out-of-bag sampling works as desired
        """


        self.data = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_oobsplit.csv'))

        self.output = self.poisson.out_of_bag_prep(self.data)

        self.assertTrue(isinstance(self.output, pd.DataFrame))

        self.assertEqual(self.output.datetime.dt.year.max(), 2018)

    def test_oob_split(self):
        """
        Test function for splitting data based on oob data
        """

        self.oobdata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_oobdata.csv'))

        self.data = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_oobsplit.csv'))

        self.train_output = self.poisson.oob_train_split(full_data=self.data, test_data=self.oobdata)

        self.assertTrue(isinstance(self.train_output, pd.DataFrame))

        self.assertEqual(2017, self.train_output.datetime.max().year)

        self.assertEqual(2016, self.train_output.datetime.min().year)

        self.assertFalse(2018 in self.train_output.datetime.dt.year.unique().tolist())

    def test_sampler(self):
        """
        Test for checking the output of the poisson sampler is as expected
        """

        self.oobdata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_oobdata.csv'))

        self.traindata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_traindata.csv'))

        self.poi_data = self.poisson.SimplePoission(train_data = self.traindata, test_data = self.oobdata, method = 'simple')

        self.assertTrue(isinstance(self.poi_data, pd.DataFrame))

        self.assertEqual(self.poi_data.columns.tolist(), ['Week','datetime','Crime_type','Counts','LSOA_code'])

        self.assertEqual(self.poi_data.Week.unique().tolist(), [26,27,28,29,30,31])

        self.assertEqual(self.poi_data.datetime.apply(lambda x: x.split('-')[0]).unique().tolist(),
                         self.oobdata.datetime.apply(lambda x: x.split('-')[0]).unique().tolist())

    def test_sampler_day_func_simp(self):
        """
        Test for checking the output of the poisson sampler is as expected
        when sampling using days
        """

        self.oobdata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_oobDay_data.csv'))

        self.traindata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_trainDay_data.csv'))

        self.poi_data = self.poisson_day.SimplePoission(train_data = self.traindata, test_data = self.oobdata, method = 'simple')

        self.assertTrue(isinstance(self.poi_data, pd.DataFrame))

        self.assertEqual(self.poi_data.columns.tolist(), ['datetime','Crime_type','Counts','LSOA_code'])

        self.assertEqual(len(self.poi_data.datetime.dt.day.unique()), 31)

    def test_sampler_day_func_zero(self):
        """
        Test for checking the output of the poisson sampler is as expected
        when sampling using days
        """

        self.oobdata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_oobDay_data.csv'))

        self.traindata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_trainDay_data.csv'))

        self.poi_data = self.poisson_day.SimplePoission(train_data = self.traindata, test_data = self.oobdata, method = 'zero')

        self.assertTrue(isinstance(self.poi_data, pd.DataFrame))

        self.assertEqual(self.poi_data.columns.tolist(), ['datetime','Crime_type','Counts','LSOA_code'])

        self.assertEqual(len(self.poi_data.datetime.dt.day.unique()), 31)

    def test_sampler_day(self):
        """
        Test for checking the output of the poisson sampler is as expected
        when sampling using days
        """

        self.oobdata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_oobDay_data.csv'))

        self.traindata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_trainDay_data.csv'))

        self.poi_data = self.poisson_day.SimplePoission(train_data = self.traindata, test_data = self.oobdata, method = 'mixed')

        self.assertTrue(isinstance(self.poi_data, pd.DataFrame))

        self.assertEqual(self.poi_data.columns.tolist(), ['datetime','Crime_type','Counts','LSOA_code'])

        self.assertEqual(len(self.poi_data.datetime.dt.day.unique()), 31)

    @patch('matplotlib.pyplot.show')
    def test_sampler_error(self, mock_show):
        """
        Testing for the error reporting function for sampler
        """
        # TODO: the double call of SimplePoission here is very labourious and may not be necessary
        # this errors on calculating rmse Input contains NaN, infinity or a value too large for dtype('float64')

        self.oobdata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_oobdata.csv'))

        self.traindata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_traindata.csv'))

        self.poi_data = self.poisson.SimplePoission(train_data = self.traindata, test_data = self.oobdata, method = 'simple')

        self.plot = self.poisson.error_Reporting(test_data = self.oobdata, simulated_data = self.poi_data)

        self.assertTrue(isinstance(self.plot, pd.DataFrame))

        self.assertEqual(self.plot.columns.tolist(), ['Week','Pred_counts','Actual','Difference'])

    @patch('matplotlib.pyplot.show')
    def test_sampler_errorDay(self, mock_show):
        """
        Testing for the error reporting function for sampler
        """
        # TODO: the double call of SimplePoission here is very labourious and may not be necessary
        # this errors on calculating rmse Input contains NaN, infinity or a value too large for dtype('float64')

        self.oobdata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_oobDay_data.csv'))

        self.traindata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_trainDay_data.csv'))

        self.poi_data = self.poisson_day.SimplePoission(train_data = self.traindata, test_data = self.oobdata, method = 'simple')

        self.plot = self.poisson.error_Reporting(test_data = self.oobdata, simulated_data = self.poi_data)

        self.assertTrue(isinstance(self.plot, pd.DataFrame))

        self.assertEqual(self.plot.columns.tolist(), ['datetime','Pred_counts','Actual','Difference'])


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

        self.assertEqual(self.descriptions.columns.tolist(), ['UID','datetime','Crime_description','Crime_type','LSOA_code','Police_force'])

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

    def test_sampler_day_agg(self):
        """
        Test for checking the output of the poisson sampler is as expected
        when sampling using days
        """

        self.oobdata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_aggoobDay_data.csv'))

        self.traindata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_aggtrainDay_data.csv'))

        self.poi_data = self.poisson_day.SimplePoission(train_data = self.traindata, test_data = self.oobdata, method = 'simple')

        self.assertTrue(isinstance(self.poi_data, pd.DataFrame))

        self.assertEqual(self.poi_data.columns.tolist(), ['datetime','Crime_type','Counts','LSOA_code'])

        self.assertEqual(len(self.poi_data.datetime.dt.day.unique()), 31)

        self.assertEqual(self.poi_data.shape[0], 14 * 31)

    def test_sampler_week_agg(self):
        """
        Test for checking the output of the poisson sampler is as expected
        """

        self.oobdata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_aggoobdata.csv'),
                                   parse_dates=['datetime'])

        self.traindata = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_aggtraindata.csv'))

        self.poi_data = self.poisson.SimplePoission(train_data = self.traindata, test_data = self.oobdata, method = 'simple')

        self.assertTrue(isinstance(self.poi_data, pd.DataFrame))

        self.assertEqual(self.poi_data.columns.tolist(), ['Week','datetime','Crime_type','Counts','LSOA_code'])

        self.assertEqual(self.poi_data.Week.unique().tolist(), [26,27,28,29,30,31])

        self.assertEqual(pd.to_datetime(self.poi_data.datetime).dt.year.unique().tolist(), self.oobdata.datetime.dt.year.unique().tolist())

        self.assertEqual(self.poi_data.shape[0], 14 * 6)

    def test_moving_window_week(self):

        self.week = 4

        self.test1 = Poisson_sim.Poisson_sim.moving_window_week(self.week, window=1)

        self.test2 = Poisson_sim.Poisson_sim.moving_window_week(self.week, window=0)

        self.test3 = Poisson_sim.Poisson_sim.moving_window_week(self.week, window=2)

        self.assertEqual(self.test1, [4, 3, 5])

        self.assertEqual(self.test2, [4])

        self.assertEqual(self.test3, [4, 3, 5, 2, 6])

    def test_moving_window_datetime(self):

        self.week = pd.to_datetime("2017-01-01")

        self.test1 = [x.strftime("%Y-%m-%d") for x in Poisson_sim.Poisson_sim.moving_window_datetime(self.week, window=1)]

        self.test2 = [x.strftime("%Y-%m-%d") for x in Poisson_sim.Poisson_sim.moving_window_datetime(self.week, window=0)]

        self.test3 = [x.strftime("%Y-%m-%d") for x in Poisson_sim.Poisson_sim.moving_window_datetime(self.week, window=2)]

        self.assertEqual(self.test1, ["2017-01-01",
                                      "2017-01-02",
                                      "2016-12-31"])

        self.assertEqual(self.test2, ["2017-01-01"])

        self.assertEqual(self.test3, ["2017-01-01",
                                      "2017-01-02",
                                      "2016-12-31",
                                      "2017-01-03",
                                      "2016-12-30"]
                                      )

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
