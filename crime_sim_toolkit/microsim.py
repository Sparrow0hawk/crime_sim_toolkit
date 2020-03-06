"""
A microsimulator class for performing the microsimulations using victim data
"""

import os
import sys
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


    def create_combined_profiles(self, demographic_cols=['sex','age','ethnicity']):
        """
        A function for combining individual demographic traits into one hyphen separated
        string.

        :param: demographic_cols list: list of strings corresponding to demographic
        trait columns

        TODO: this could be a staticmethod? That is subsequently called within other functions
              in the class workflow
        """

        self.crime_data['victim_profile'] = self.crime_data[demographic_cols].astype(str).apply('-'.join ,axis=1)


    def generate_probability_table(self,):
        """
        Generate a probability table of chance of specific crime description occuring
        to person of specific demographic class on a given day in a given month

        : param: synthetic_population_dir string: a string of the path to a directory containing
                 spenser synthetic population data
        """

        self.crime_data.groupby(['Month','victim_profile','Crime_description'])['Crime_description'].count()
        # START HERE refer to hackmd notes
