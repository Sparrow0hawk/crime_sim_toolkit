# TODO: do we build lots of little methods that are called by a big method?
#       or a series of class methods that are called sequentially?

# import libraries
import glob
from calendar import monthrange
import pandas as pd
import numpy as np


class Initialiser:
    """
    Functionality for building simple poisson sampling crime data generator
    Requires data from https://data.police.uk/ in data folder
    """

    def __init__(self, LA_names):

        self.LA_names = LA_names

        # boot up LSOA lists from 2011 census
        LSOA_pop = pd.read_csv('./src/LSOA_data/census_2011_population_hh.csv')

        LSOA_pop = LSOA_pop[LSOA_pop['Local authority name'].isin(LA_names)]

        LSOA_counts = LSOA_pop[['LSOA Code','LSOA Name','Persons','Households']].reset_index(drop=True)

        LSOA_counts.columns = ['LSOA_code','LSOA_name','persons','households']

        LSOA_counts.persons = LSOA_counts.persons.apply(lambda x: np.int64(x.replace(',', '')))

        LSOA_counts.households = LSOA_counts.households.apply(lambda x: np.int64(x.replace(',', '')))

        self.LSOA_hh_counts = LSOA_counts

    def get_data(self, timeframe='Week'):
        """
        One-caller function that loads and manipulates data ready for use
        """

        print('Fetching count data from police reports.')
        print('Sit back and have a brew, this may take sometime.')
        print(' ')

        # this initialises two class variables
        self.initialise_data()

        dated_data = self.random_date_allocate(data=self.report_frame, timeframe=timeframe)

        mut_counts_frame = self.reports_to_counts(dated_data, timeframe=timeframe)

        mut_counts_frame = self.add_zero_counts(mut_counts_frame)

        return mut_counts_frame

    def initialise_data(self):
        """
        Function to initialise dataset

        This will load data from the embedded data folder (src) and user passed dataset

        Input: src folder
               data folder: populated with monthly csv files from custom downloads from https://data.police.uk/data/

        TODO: build some tests
              Does it return data with right columns? Does it match an expected length after concat?
              Can you return certain LSOA household value etc
        """

        # section for pulling in and concatenating police report data
        # adding if block that will search for data in data folder
        # if none found default to using test data in tests folder
        files_list = glob.glob('data/policedata*/*/*.csv')

        print('Number of data files found: ', str(len(files_list)))

        if len(files_list) == 0:
            print('No files found in data folder.')
            print('Defaulting to test data.')
            files_list = glob.glob('tests/testing_data/test_policedata/*/*.csv')

        files_combo = []

        for file in files_list:

            open_file = pd.read_csv(file)

            files_combo.append(open_file)

        combined_files = pd.concat(files_combo, axis=0)

        combined_files.reset_index(inplace=True, drop=True)

        self.report_frame = combined_files

        return 'Data Loaded.'

    @classmethod
    def random_date_allocate(cls, data, timeframe='Week'):
        """
        function for randomly allocating Days or weeks to police data
        """

        try:
            data['Month'] == True
        except KeyError:
            print('Your data does not appear to have a month column.')
            print('Please try again with Month in a Year-Month format.')
            return False

        dated_data = data.copy()

        # extract year from Month column
        dated_data['Year'] = dated_data['Month'].map(lambda x: pd.to_datetime(x).year)

        # extract month from Month column
        dated_data['Mon'] = dated_data['Month'].map(lambda x: pd.to_datetime(x).month)

        # randomly allocate day for crime report
        # based on np.randint selecting from a range from 1 to the maximum number of days
        # in the given month in the given year
        dated_data['Day'] = dated_data['Month'].map(lambda x: np.random.randint(1,monthrange(pd.to_datetime(x).year, pd.to_datetime(x).month)[1] +1))

        print('Psuedo days allocated to all reports.')

        # are weeks required?
        if timeframe == 'Week':
            # get week of the year based on month, year and psuedo-day allocated above
            # we're converting all separated columns to datetime format and extract week number
            dated_data['Week'] = dated_data.apply(lambda x: pd.to_datetime([str(x.Year)+'/'+str(x.Mon)+'/'+str(x.Day)]).week[0], axis=1)

            print('Week numbers allocated.')

        return dated_data

    def reports_to_counts(self, reports_frame, timeframe='Week'):
        """
        function to convert policedata from individal reports level to aggregate counts at time scale, LSOA, crime type
        """

        # right both data sets are ready for the generation of transition probabilities of crime in each LSOA

        counts_frame = pd.DataFrame(reports_frame.groupby(['Year','Mon','Crime type','LSOA code'])[timeframe].value_counts()).reset_index(level=['Mon','Crime type','Year','LSOA code'])

        counts_frame.columns = ['Year', 'Mon', 'Crime_type','LSOA_code', 'Counts']

        counts_frame.reset_index(inplace=True)

        # filter for just WY LSOA

        counts_frame = counts_frame[counts_frame.LSOA_code.isin(self.LSOA_hh_counts.LSOA_code)]

        counts_frame.reset_index(inplace=True, drop=True)

        return counts_frame

    def add_zero_counts(self, counts_frame):
        """
        Function to include of zero crime to date-allocated crime counts dataframe
        """
        # test if psuedo-Weeks have been allocated

        pile_o_df = []

        if 'Week' in counts_frame.columns:
            time_res = 'Week'
        else:
            time_res = 'Day'

        for year in counts_frame.Year.unique():

            year_frame = counts_frame.copy()

            year_frame = year_frame[year_frame.Year == year]

            for month in counts_frame.Mon.unique():

                # for either day or week in temp resolution provided
                for wk in year_frame[time_res].unique():

                    wk_frame = year_frame[(year_frame[time_res].values == wk) & (year_frame.Mon.values == month)]

                # only crime types within existing data

                    for crim_typ in counts_frame['Crime_type'].unique():

                        sliced_frame = wk_frame[wk_frame.Crime_type == crim_typ]

                        missing_LSOA = self.LSOA_hh_counts.LSOA_code[~self.LSOA_hh_counts.LSOA_code.isin(sliced_frame.LSOA_code)].tolist()

                        new_fram = pd.DataFrame(missing_LSOA, columns=['LSOA_code'], index=range(len(missing_LSOA)))

                        new_fram['Crime_type'] = crim_typ

                        new_fram['Counts'] = 0

                        new_fram['Mon'] = month

                        new_fram[time_res] = wk

                        new_fram['Year'] = year

                        pile_o_df.append(new_fram)


        new_tot_counts = pd.concat([counts_frame,pd.concat(pile_o_df)], sort=True)

        new_tot_counts.reset_index(drop=True, inplace=True)

        return new_tot_counts
