# TODO: do we build lots of little methods that are called by a big method?
#       or a series of class methods that are called sequentially?

# import libraries
import sys
import math
import glob
from calendar import monthrange
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats


class Initialiser:
    """
    Functionality for building simple poisson sampling crime data generator
    Requires data from https://data.police.uk/ in data folder
    """

    def __init__(self):
        pass



    def initialise_data(self, LA_names):
        """
        Function to initialise dataset

        This will load data from the embedded data folder (src) and user passed dataset

        Input: LA_names : local authority names, python list of capitalised strings of local authority names
               src folder
               data folder: populated with monthly csv files from custom downloads from https://data.police.uk/data/

        TODO: build some tests
              Does it return data with right columns? Does it match an expected length after concat?
              Can you return certain LSOA household value etc
        """

        # boot up LSOA lists from 2011 census

        LSOA_pop = pd.read_csv('./src/census_2011_population_hh.csv')

        LSOA_pop = LSOA_pop[LSOA_pop['Local authority name'].isin(LA_names)]

        LSOA_counts = LSOA_pop[['LSOA Code','LSOA Name','Persons','Households']].reset_index(drop=True)

        LSOA_counts.columns = ['LSOA_code','LSOA_name','persons','households']

        LSOA_counts.persons = LSOA_counts.persons.apply(lambda x: np.int64(x.replace(',', '')))

        LSOA_counts.households = LSOA_counts.households.apply(lambda x: np.int64(x.replace(',', '')))

        # section for pulling in and concatenating police report data
        files_list = glob.glob('data/policedata*/*/*.csv')

        files_combo = []

        for file in files_list:

            open_file = pd.read_csv(file)

            files_combo.append(open_file)

        combined_files = pd.concat(files_combo, axis=0)

        combined_files.reset_index(inplace=True, drop=True)

        self.report_frame = combined_files

        self.LSOA_hh_counts = LSOA_counts

        return 'Data Initialised.'

    def random_date_allocate(self, data, Week=False):
        """
        function for randomly allocating Days or weeks to police data
        """
        try:
            data['Month'] == True
        except KeyError:
            print('Your data does not appear to have a month column.')
            print('Please try again with Month in a Year-Month format.')
            return False
            sys.exit()


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
        if Week == True:
            # get week of the year based on month, year and psuedo-day allocated above
            # we're converting all separated columns to datetime format and extract week number
            dated_data['Week'] = dated_data.apply(lambda x: pd.to_datetime([str(x.Year)+'/'+str(x.Mon)+'/'+str(x.Day)]).week[0], axis=1)

            print('Week numbers allocated.')

        return dated_data

    def reports_to_counts(self, reports_frame, timeframe='Day'):
        """
        function to convert policedata from individal reports level to aggregate counts at time scale, LSOA, crime type
        """

        # right both data sets are ready for the generation of transition probabilities of crime in each LSOA

        counts_frame = pd.DataFrame(reports_frame.groupby(['Year','Mon','Crime type','LSOA code'])[timeframe].value_counts()).reset_index(level=['Mon','Crime type','Year','LSOA code'])

        print(counts_frame.columns)

        counts_frame.columns = ['Year', 'Mon', 'Crime_type','LSOA_code', 'Counts']

        counts_frame.reset_index(inplace=True)

        # filter for just WY LSOA

        counts_frame = counts_frame[counts_frame.LSOA_code.isin(LSOA_counts_WY.LSOA_code)]

        counts_frame.reset_index(inplace=True, drop=True)

        counts_frame.head()

        counts_frame.LSOA_code.isin(LSOA_counts_WY.LSOA_code).shape

        LSOA_counts_WY.LSOA_code.unique().shape

        frame1 = tot_counts[tot_counts.Year == 2016]

        frame1 = frame1[frame1.Week == 33]

        frame1.head()


    def add_zero_counts(self):
        """
        Function to include of zero crime to date-allocated crime counts dataframe
        """
        pile_o_df = []

        for year in tot_counts.Year.unique():

            year_frame = tot_counts.copy()

            year_frame = year_frame[year_frame.Year == year]

            for wk in year_frame.Week.unique():

                wk_frame = year_frame[year_frame.Week == wk]

                for crim_typ in tot_counts['Crime_type'].unique():

                    sliced_frame = wk_frame[wk_frame.Crime_type == crim_typ]

                    missing_LSOA = LSOA_counts_WY.LSOA_code[~LSOA_counts_WY.LSOA_code.isin(sliced_frame.LSOA_code)].tolist()

                    new_fram = pd.DataFrame(missing_LSOA, columns=['LSOA_code'], index=range(len(missing_LSOA)))

                    new_fram['Crime_type'] = crim_typ

                    new_fram['Counts'] = 0

                    new_fram['Mon'] = sliced_frame.Mon.unique().tolist()[0]

                    new_fram['Week'] = sliced_frame.Week.unique().tolist()[0]

                    new_fram['Year'] = sliced_frame.Year.unique().tolist()[0]

                    pile_o_df.append(new_fram)


        new_tot_counts = pd.concat([tot_counts,pd.concat(pile_o_df)], sort=True)

        new_tot_counts.reset_index(drop=True, inplace=True)


# check whether each week has the same number of unique LSOAs (indicating zero results have been filled in)
    def zeros_check(self):
        """
        Function to print out number of unique LSOAs per timeframe (week/day)
        Checks that LSOAs with zero crime have been included
        TODO: unclear if needed or should be formatted into test
        """
        for year in new_tot_counts.Year.unique():

            print(year)

            year_frame = new_tot_counts.copy()

            year_frame = year_frame[year_frame.Year == year]

            for wk in year_frame.Week.unique():

                wk_frame = year_frame[year_frame.Week == wk]

                print('For week: '+str(wk)+' number of unique LSOAs: '+str(len(wk_frame.LSOA_code.unique())))
