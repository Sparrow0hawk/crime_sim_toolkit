"""
A microsimulator class for performing the microsimulations using victim data
"""

import os
import sys
import glob
import pandas as pd
import numpy as np
from crime_sim_toolkit import utils
import multiprocessing as mp

class Microsimulator():
    """
    A class for initialising data on victimisation for the simulation.
    Includes some validation tests to ensure user has passed a real file path,
    and the seed year specified matches data passed.

    """

    def __init__(self):

        return

    def load_data(self, seed_year: int, police_data_dir: str, seed_pop_dir: str,
                  spenser_demographic_cols: list, police_demographic_cols: list):
        """
        A wrapper function that loads police data and seed population data

        :param: seed_year int:
        :param: police_data_dir str:
        :param: seed_pop_dir str:
        :param: spenser_demographic_cols list:
        :param: police_demographic_cols list:
        """

        self.load_crime_data(year=seed_year, directory=police_data_dir, demographic_cols=police_demographic_cols)

        self.load_seed_pop(seed_population_dir=seed_pop_dir, demographic_cols=spenser_demographic_cols)

    def load_crime_data(self, year: int, directory: str, demographic_cols: list):
        """
        Load individual police crime reports with victims data into
        Microsimulator object

        :param: year int: specify seed year of victim data
        :param: directory str: string of full path to data
        :param: demographic_cols list: suggested preset ['sex','age','ethnicity']

        """

        if os.path.isfile(directory):

            self.crime_data = pd.read_csv(directory)

        else:
            print('File does not exist.')
            print('Please check the directory you passed: \n',directory)
            sys.exit(0)

        # set internal check that the year is the same for the entire
        # dataframe

        # extract month string col which contains year-mon format
        # split string by hyphen and expand to two columns
        # select first col at 0 index and get unique entries
        # then convert to int and calculate the mean
        # if only 1 unique year should give round number as mean i.e. 2017.0
        dat_year = self.crime_data.Month.str.split('-', expand=True)[0].unique().astype(int).mean()

        if dat_year != year:

            print('Warning: The year in the dataframe does not match the passed seed year')
            print('Passed seed year: ',year,' dataframe year: ',dat_year)

        # create demographic_profile column, using default columns

        self.crime_data = self.create_combined_profiles(self.crime_data, demographic_cols=demographic_cols)


    def create_combined_profiles(self, dataframe, demographic_cols: list):
        """
        A function for combining individual demographic traits into one hyphen separated
        string.

        :param: dataframe pd.DataFrame: a pandas dataframe containing demographic cols
        :param: demographic_cols list: list of strings corresponding to demographic
        trait columns, suggested preset ['sex','age','ethnicity']

        TODO: this could be a staticmethod? That is subsequently called within other functions
              in the class workflow
        """

        try:

            dataframe['demographic_profile'] = dataframe[demographic_cols].astype(str).apply('-'.join ,axis=1)

            return dataframe

        except KeyError:

            raise KeyError('Column names passed ('+' '.join(demographic_cols)+') do not match column names in dataframe.')

    def generate_probability_table(self):
        """
        Generate a probability table of chance of specific crime description occuring
        to person of specific demographic class on a given day in a given month

        """

        # groupby crime_data by month, victim profile and crime description
        # then count the number of each Crime_description in those groups
        crimes_grouped = self.crime_data.groupby(['Month','demographic_profile','Crime_description'])['Crime_description'].count()

        crimes_grouped = crimes_grouped.reset_index(['Month','demographic_profile'])

        crimes_grouped.columns = ['Month','demographic_profile','crime_counts']

        crimes_grouped.reset_index(inplace=True)

        # get counts of each demographic group in seed population
        population_grp_counts = self.seed_population.demographic_profile.value_counts().reset_index()

        population_grp_counts.columns = ['demographic_profile','demo_group_counts']

        # create a dict of population-group-ids and counts of those groups
        pop_group_dict = population_grp_counts.set_index('demographic_profile')['demo_group_counts'].to_dict()

        # map the dictionary onto the demographic profiles column in crimes dataframe to get populations
        crimes_grouped['demo_group_counts'] = crimes_grouped.demographic_profile.map(pop_group_dict)

        # assign this to a new variable
        crime_and_pop = crimes_grouped

        # calculate rate of crime within population for a given month and demographic group
        crime_and_pop['crime_count_per_pop'] = crime_and_pop.crime_counts / crime_and_pop.demo_group_counts

        crime_and_pop['day_in_month'] = crime_and_pop['Month'].map(utils.days_in_month_dict(crime_and_pop))
        # divide the rate of crime within population/ month/ demographic group by
        # number of days in month to give rate of crime within population/monht/demographic group/day
        crime_and_pop['chance_crime_per_day_demo'] = crime_and_pop['crime_count_per_pop'] / crime_and_pop['day_in_month']

        # for rows with 0 in their demographic subpopulation we get NaNs to solve this we'll convert them all to 0
        crime_and_pop['chance_crime_per_day_demo'] = crime_and_pop['chance_crime_per_day_demo'].fillna(0)

        # set this final table as transition_table
        self.transition_table = crime_and_pop[['Crime_description','Month','day_in_month',
                                               'demographic_profile','crime_counts',
                                               'chance_crime_per_day_demo']]


    def load_seed_pop(self, seed_population_dir: str, demographic_cols: list):
        """
        A function for loading the specific seed population for generating
        transition probailities.

        : param: seed_population_dir string: a string of the path to the SPENSER synthetic population
                 file
        : param: demographic_cols list: list of strings corresponding to demographic
                 trait columns - suggest to use spenser columns ['DC1117EW_C_SEX','DC1117EW_C_AGE','DC2101EW_C_ETHPUK11']
        """

        self.seed_population = pd.read_csv(seed_population_dir)

        self.seed_population = self.create_combined_profiles(self.seed_population,
                                                        demographic_cols=demographic_cols)


    def load_future_pop(self, synthetic_population_dir: str, year: int, demographic_cols: list):
        """
        A function for loading the synthetic future populations

        : param: synthetic_population_dir string: a string of the path to a directory containing
                 spenser synthetic population data expects path to end in /
        : param: year int: a integer the year of the synthetic population that
                 the user wishes to load
        : param: demographic_cols list: list of strings corresponding to demographic
                 trait columns - suggest to use spenser columns ['DC1117EW_C_SEX','DC1117EW_C_AGE','DC2101EW_C_ETHPUK11']
        """

        # section for testing if synthetic_population_dir ends in /

        if synthetic_population_dir[-1] != '/':

            synthetic_population_dir += '/'

        # create a file list of all files containing year
        file_list = glob.glob(str(synthetic_population_dir)+'*'+str(year)+'*.csv')

        # we need to combine files from spenser into the police force area
        # this assumes spenser files are from local authority areas within the same
        # police force area

        try:
            files_combo = []

            for file in file_list:

                open_file = pd.read_csv(file)

                files_combo.append(open_file)

            combined_files = pd.concat(files_combo, axis=0)

            self.future_population = combined_files.reset_index(inplace=True, drop=True)

            self.future_population = combined_files

            self.future_population = self.create_combined_profiles(self.future_population,
                                                            demographic_cols=demographic_cols)

        except ValueError as e:

            raise type(e)(str(e) + '\nNo data files to load. Following files found in directory passed: '+str(file_list))


    def run_simulation(self, future_population):
        """
        A function that takes loaded transition table and a future population and
        simulates a years worth of crime based on transition table

        :param: future_population pd.DataFrame: dataframe of future population
        """
        results = {'Month' : [],
                   'Day' : [],
                   'Person' : [],
                   'crime' : []
                   }

        # for each month in transition table of crime probability
        for month in self.transition_table.Month.unique():

            # create a specific table for the given month
            month_trans_table = self.transition_table[self.transition_table.Month.isin([month])]

            # for each crime in Crime_description of crime table
            for crime in month_trans_table.Crime_description.unique():

                # narrow table to the given crime in the given month
                month_crime = month_trans_table[month_trans_table.Crime_description.isin([crime])]

                # create a dictionary of each demographic profile and their risk
                cond_dict = month_crime[['demographic_profile','chance_crime_per_day_demo']]\
                            .set_index('demographic_profile')['chance_crime_per_day_demo'].to_dict()

                # run a simulation for each day in the given month
                for day in range(1, month_trans_table.day_in_month.unique()[0] + 1):

                    # create a boolean mask for each person in the future population
                    # this corresponds to a 1 or 0 generated from randomly sampling based on
                    # demographic probability of being victimised by the given crime
                    # if not in that demographic return False
                    # if True returns means that person was victimised
                    bool_mask = future_population.demographic_profile.apply( \
                                            lambda x: bool(int(np.random.choice([1,0], \
                                                                                p=[cond_dict.get(x), \
                                                                                1 - cond_dict.get(x)] \
                                                                                ))) \
                                                                                if cond_dict.get(x) is not None else False
                                                                                )

                    # slice future population array by generated boolean mask
                    masked_victim_pop = future_population[bool_mask]

                    # if that sliced array has greater than 0 rows
                    # append data to results dict
                    if masked_victim_pop.shape[0] != 0:
                      
                        results['Month'].append(month.split("-")[1])

                        results['Day'].append(day)

                        results['Person'].append(masked_victim_pop.PID.tolist())

                        results['crime'].append(crime)

        # create dataframe from result dict
        results_frame = pd.DataFrame.from_dict(results)

        # explode person row into a row per person in returned list
        results_frame = results_frame.explode('Person')

        # set class variable
        return results_frame


    def run_mp_simulation(self):
        """
        A method for performing the simulation using multiprocessing
        to chunk the population dataset and run multiple simulations in
        parrallel on each chunk of data before recombining them into the final
        output

        :param: nprocs int: number of processors avaiable to use
        """

        nprocs = mp.cpu_count()

        # split data into chunks based on number of processors
        split_data = np.array_split(self.future_population, nprocs)

        results = []

        pool = mp.Pool(processes=nprocs)

        results += pool.map(self.run_simulation, split_data)

        return pd.concat(results)
