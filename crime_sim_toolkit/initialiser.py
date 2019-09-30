# TODO: do we build lots of little methods that are called by a big method?
#       or a series of class methods that are called sequentially?

# import libraries
import sys
import glob
from calendar import monthrange
import pandas as pd
import numpy as np
import pkg_resources
from crime_sim_toolkit import utils

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

        self.PolForce_LSOA_map = pd.read_csv(pkg_resources.resource_filename(resource_package, 'src/LSOA_data/PoliceforceLSOA.csv'),
                                        index_col=0)

    def get_data(self, directory=None, timeframe='Week', aggregate=False):
        """
        One-caller function that loads and manipulates data ready for use

        arguments:
          directory = directory containing folders for each month of crime data. Default None (passes test_dir)

          timeframe = the desired timeframe of data. Either Week or Day. Default Week.

          aggregate = boolean: do you wish to aggregate data to police force area. Default false.
        """

        print(' ')
        print('Fetching count data from police reports.')
        print('Sit back and have a brew, this may take sometime.')
        print(' ')

        # this initialises two class variables
        self.initialise_data(directory=directory)

        dated_data = self.random_date_allocate(data=self.report_frame)

        mut_counts_frame = self.reports_to_counts(dated_data, aggregate=aggregate)

        # is aggregate is not true then LSOA codes will be used by default
        # therefore add_zero_counts should be used
        if aggregate != True:

            mut_counts_frame = self.add_zero_counts(mut_counts_frame, timeframe=timeframe)

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
    def random_date_allocate(cls, data):
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

        #### REFACTOR STARTS HERE

        # create a datetime column that captures month, year from Month column
        # and adds a randomly allocated day based on year+month
        # adds this as a new datetime column
        dated_data['datetime'] = dated_data.apply(lambda x: pd.to_datetime(
                                    x.Month+'/'+str(
                                    np.random.randint(1, monthrange(
                                                    pd.to_datetime([x.Month]).year[0],
                                                    pd.to_datetime([x.Month]).month[0])[1] +1))
                                                    ),
                                                    axis=1)

        print('Psuedo days allocated to all reports.')

        return dated_data

    def reports_to_counts(self, reports_frame, aggregate=False):
        """
        function to convert policedata from individal reports level to aggregate counts at time scale, LSOA, crime type
        """

        # right both data sets are ready for the generation of transition probabilities of crime in each LSOA

        # function to ensure datetime is datetime dtype
        reports_frame = utils.validate_datetime(reports_frame)

        counts_frame = pd.DataFrame(reports_frame.groupby(['Crime type','LSOA code'])['datetime'].value_counts()).reset_index(level=['Crime type','LSOA code'])

        counts_frame.columns = ['Crime_type','LSOA_code', 'Counts']

        # get datetime out of index
        counts_frame.reset_index(inplace=True)

        counts_frame = counts_frame[counts_frame.LSOA_code.isin(self.LSOA_hh_counts.LSOA_code)]

        # if aggregate is true convert LSOA_code column to police force area name
        if aggregate == True:

            # map LSOAs to police force area
            counts_frame['LSOA_code'] = counts_frame.LSOA_code.map(lambda x: self.PolForce_LSOA_map[self.PolForce_LSOA_map['LSOA Code'].isin([x])].Police_force.tolist()[0])

            # group columns by Police force for crime type and date and sum the counts column
            # thus aggregating data into the new police force category
            counts_frame = counts_frame.groupby(['datetime','Crime_type','LSOA_code'])['Counts'].sum().reset_index(['datetime','Crime_type','LSOA_code'])

        counts_frame.reset_index(inplace=True, drop=True)

        return counts_frame

    def add_zero_counts(self, counts_frame, timeframe='Week'):
        """
        Function to include of zero crime to date-allocated crime counts dataframe
        """
        # test if psuedo-Weeks have been allocated

        # lists for data to be appended to
        lsoa_lst = []
        crime_lst = []
        counts_lst = []
        timeres_lst = []

        # function to ensure datetime is datetime dtype
        sliced_frame = utils.validate_datetime(counts_frame.copy())

        for date in counts_frame['datetime'].unique():

            narrow_frame = sliced_frame[sliced_frame['datetime'].isin([date])]

            for crim_typ in counts_frame['Crime_type'].unique():

                final_nar_frame = narrow_frame[narrow_frame.Crime_type.isin([crim_typ])]

                missing_LSOA = self.LSOA_hh_counts.LSOA_code[~self.LSOA_hh_counts.LSOA_code.isin(final_nar_frame.LSOA_code)].tolist()

                missing_len = len(missing_LSOA)

                # add values to lists
                # for values with one instance multiple by number of missing_LSOA to get
                # correct dimensions
                lsoa_lst += missing_LSOA
                crime_lst += [crim_typ] * missing_len
                counts_lst += [0] * missing_len
                timeres_lst += [date] * missing_len


        missing_dataf = pd.DataFrame.from_dict({'LSOA_code' : lsoa_lst,
                                                 'Crime_type': crime_lst,
                                                 'datetime' : timeres_lst,
                                                 'Counts' : counts_lst})

        new_tot_counts = pd.concat([counts_frame, missing_dataf], sort=True)

        ## new section for adding Weeks

        if timeframe == 'Week':
        # get week of the year based on month, year and psuedo-day allocated above
        # we'll just extract it from the datetime object created above
            new_tot_counts['Week'] = new_tot_counts.apply(lambda x: x.datetime.week, axis=1)

            new_tot_counts['datetime'] = new_tot_counts.datetime.apply(lambda x: x.strftime('%Y-%m'))

            new_tot_counts = pd.DataFrame(new_tot_counts.groupby(['datetime','Crime_type','LSOA_code'])['Week'].value_counts()).reset_index(level=['datetime','Crime_type','LSOA_code'])

            new_tot_counts.columns = ['datetime','Crime_type','LSOA_code', 'Counts']

            # get datetime out of index
            new_tot_counts.reset_index(inplace=True)

            print('Week numbers allocated.')


        new_tot_counts.reset_index(inplace=True, drop=True)

        return new_tot_counts
