"""
A series of classes that work to sample crime events based on
a synthetic population and victimisation data
"""

import os
import sys
import pandas as pd

class VictimData():
    """
    A class for initialising data on victimisation for the simulation.
    
    :param: year int: specify seed year of victim data
    :param: directory str: string of full path to data

    """

    def __init__(self, year: int, directory: str):

        self.year = year

        self.directory = directory

    def load_data(self):
        """
        Handle loading data from alternate sources.
        If user does not have local CSEW data, can fall back on police reported
        data
        """

        if os.path.isfile(self.directory):

            victim_data = pd.read_csv(self.directory)

        else:
            print('File does not exist.')
            print('Please check the directory you passed: \n',self.directory)
            sys.exit(0)

        # set internal check that the year is the same for the entire
        # dataframe

        # extract month string col which contains year-mon format
        # split string by hyphen and expand to two columns
        # select first col at 0 index and get unique entries
        # then convert to int and calculate the mean
        # if only 1 unique year should give round number as mean i.e. 2017.0
        dat_year = victim_data.Month.str.split('-', expand=True)[0].unique().astype(int).mean()

        if dat_year != self.year:

            print('Warning: The year in the dataframe does not match the passed seed year')
            print('Passed seed year: ',self.year,' dataframe year: ',dat_year)

        return victim_data
