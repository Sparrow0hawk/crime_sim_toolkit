# TODO: do we build lots of little methods that are called by a big method?
#       or a series of class methods that are called sequentially?

# import libraries
import sys
import glob
from calendar import monthrange
import pandas as pd
import numpy as np
import pkg_resources

# Could be any dot-separated package/module name or a "Requirement"
resource_package = 'crime_sim_toolkit'


class Initialiser:
    """
    Functionality for building simple poisson sampling crime data generator
    Requires data from https://data.police.uk/ in data folder
    """

    def __init__(self, LA_names):

        self.LA_names = LA_names

        # boot up LSOA lists from 2011 census
        LSOA_pop = pd.read_csv(pkg_resources.resource_filename(resource_package, 'src/LSOA_data/census_2011_population_hh.csv'))

        LSOA_pop = LSOA_pop[LSOA_pop['Local authority name'].isin(LA_names)]

        LSOA_counts = LSOA_pop[['LSOA Code','LSOA Name','Persons','Households']].reset_index(drop=True)

        LSOA_counts.columns = ['LSOA_code','LSOA_name','persons','households']

        LSOA_counts.persons = LSOA_counts.persons.apply(lambda x: np.int64(x.replace(',', '')))

        LSOA_counts.households = LSOA_counts.households.apply(lambda x: np.int64(x.replace(',', '')))

        self.LSOA_hh_counts = LSOA_counts

    def get_data(self, directory=None, timeframe='Week'):
        """
        One-caller function that loads and manipulates data ready for use
        """

        print('Fetching count data from police reports.')
        print('Sit back and have a brew, this may take sometime.')
        print(' ')

        # this initialises two class variables
        self.initialise_data(directory=directory)

        dated_data = self.random_date_allocate(data=self.report_frame, timeframe=timeframe)

        mut_counts_frame = self.reports_to_counts(dated_data, timeframe=timeframe)

        mut_counts_frame = self.add_zero_counts(mut_counts_frame)

        return mut_counts_frame

    def initialise_data(self, directory=None):
        """
        Function to initialise dataset

        This will load data from the embedded data folder (src) and user passed dataset

        Input: src folder
               directory: string path to directory with nested month folders with police data

        """

        files_list = glob.glob(str(directory)+'/*/*.csv')

        print('Number of data files found: ', str(len(files_list)))

        if directory == None:
            print('No directory passed.')
            print('Defaulting to test data.')
            files_list = glob.glob(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_policedata/')+'*/*.csv')

        else:
            if len(files_list) == 0:

                print('No files found. Please ensure you have specified the correct path.')
                print('Glob has searched for '+directory+'/*/*.csv')
                sys.exit(0)

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

        # lists for data to be appended to
        lsoa_lst = []
        crime_lst = []
        counts_lst = []
        mon_lst = []
        year_lst = []
        timeres_lst = []

        if 'Week' in counts_frame.columns:
            time_res = 'Week'
        else:
            time_res = 'Day'

        for year in counts_frame.Year.unique():

            year_frame = counts_frame.copy()

            year_frame = year_frame[year_frame.Year == year]

            for month in counts_frame.Mon.unique():

                # for either day or week in temp resolution provided
                for wk in year_frame[year_frame.Mon == month][time_res].unique():

                    wk_frame = year_frame[(year_frame[time_res].values == wk) & (year_frame.Mon.values == month)]

                # only crime types within existing data

                    for crim_typ in counts_frame['Crime_type'].unique():

                        sliced_frame = wk_frame[wk_frame.Crime_type == crim_typ]

                        missing_LSOA = self.LSOA_hh_counts.LSOA_code[~self.LSOA_hh_counts.LSOA_code.isin(sliced_frame.LSOA_code)].tolist()

                        missing_len = len(missing_LSOA)

                        # add values to lists
                        # for values with one instance multiple by number of missing_LSOA to get
                        # correct dimensions
                        lsoa_lst += missing_LSOA
                        crime_lst += [crim_typ] * missing_len
                        counts_lst += [0] * missing_len
                        mon_lst += [month] * missing_len
                        year_lst += [year] * missing_len
                        timeres_lst += [wk] * missing_len


        missing_dataf = pd.DataFrame.from_dict({'LSOA_code' : lsoa_lst,
                                                 'Crime_type': crime_lst,
                                                 'Year': year_lst,
                                                 'Mon' : mon_lst,
                                                 time_res : timeres_lst,
                                                 'Counts' : counts_lst})

        new_tot_counts = pd.concat([counts_frame, missing_dataf], sort=True)

        return new_tot_counts
