"""
A series of classes that work to sample crime events based on
a synthetic population and victimisation data
"""


import pandas as pd
from crime_sim_toolkit.initialiser import Initialiser

class VictimData(Initialiser):
    """
    A class for initialising data on victimisation for the simulation.
    Inherits from Initialiser class on the instance that victimisation must be
    infered from reported police data.

    :param: CSEW bool: querying if user is using CSEW data
    :param: year int: specify seed year of victim data
    :param: directory str: string of full path to data

    """

    def __init__(self, CSEW: boolean, year: int, directory: str):

        self.CSEW = CSEW


    def load_data(self):
        """
        Handle loading data from alternate sources.
        If user does not have local CSEW data, can fall back on police reported
        data
        """

        if self.CSEW is True:

            vicData = pd.read_csv(directory)

        else:

            vicData = self.infer_victim_data(year, directory)
