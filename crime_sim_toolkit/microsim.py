"""
A microsimulator class for performing the microsimulations using victim data
"""

import os
import sys
import glob
import pandas as pd

class Microsimulator():
    """
    A class for initialising data on victimisation for the simulation.
    Includes some validation tests to ensure user has passed a real file path,
    and the seed year specified matches data passed.

    """

    def __init__(self):

        return

    def load_data(self, year: int, directory: str):
        """
        Load individual police crime reports with victims data into
        Microsimulator object

        :param: year int: specify seed year of victim data
        :param: directory str: string of full path to data

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

        # create victim_profile column, using default columns

        self.crime_data = self.create_combined_profiles(self.crime_data, demographic_cols=['sex','age','ethnicity'])


    def create_combined_profiles(self, dataframe, demographic_cols=['sex','age','ethnicity']):
        """
        A function for combining individual demographic traits into one hyphen separated
        string.

        :param: dataframe pd.DataFrame: a pandas dataframe containing demographic cols
        :param: demographic_cols list: list of strings corresponding to demographic
        trait columns

        TODO: this could be a staticmethod? That is subsequently called within other functions
              in the class workflow
        """

        try:

            dataframe['victim_profile'] = dataframe[demographic_cols].astype(str).apply('-'.join ,axis=1)

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
        self.crime_data.groupby(['Month','victim_profile','Crime_description'])['Crime_description'].count()


    def load_seed_pop(self, seed_population_dir: str, demographic_cols=['DC1117EW_C_SEX','DC1117EW_C_AGE','DC2101EW_C_ETHPUK11']):
        """
        A function for loading the specific seed population for generating
        transition probailities.

        : param: seed_population_dir string: a string of the path to the SPENSER synthetic population
                 file
        : param: demographic_cols list: list of strings corresponding to demographic
        trait columns - preset to default to spenser column names
        """

        self.seed_population = pd.read_csv(seed_population_dir)

        self.seed_population = self.create_combined_profiles(self.seed_population,
                                                        demographic_cols=demographic_cols)


    def load_future_pop(self, synthetic_population_dir: str, year: int):
        """
        A function for loading the synthetic future populations

        : param: synthetic_population_dir string: a string of the path to a directory containing
                 spenser synthetic population data expects path to end in /

        : param: year int: a integer the year of the synthetic population that
                 the user wishes to load
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

        except ValueError as e:

            raise type(e)(str(e) + '\nNo data files to load. Following files found in directory passed: '+str(file_list))