# TODO: this section will simply be for the poisson sampler code
# it will call out to a separate initialiser function to actually get data

# import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from sklearn.metrics import mean_squared_error, median_absolute_error, mean_absolute_error
from crime_sim_toolkit.initialiser import Initialiser


class Poisson_sim:
    """
    Functionality for building simple poisson sampling crime data generator
    Requires data from https://data.police.uk/ in data folder
    """

    def __init__(self, LA_names, timeframe='Week'):

        self.data = Initialiser(LA_names=LA_names).get_data(directory=None, timeframe=timeframe)

    @classmethod
    def out_of_bag_prep(cls, full_data):
        """
        Function for selecting out a year of real data from counts data for
        out-of-bag sampler comparison

        Input: Pandas dataframe of crime counts in format from initialiser | can pass class instance

        Output: Pandas dataframe of crime counts for maximum year in dataset to be held as out of bag test set
        """

        original_frame = full_data

        # identify highest year with complete counts for entire year
        # this will be used as out-of-bag comparator
        try:
            oob_year = original_frame.Year.unique()[original_frame.groupby('Year')['Mon'].unique().map(lambda x: len(x) == 12)].max()

        except ValueError:
            print('The passed data does not appear to have a full years (Jan-Dec) worth of data.')
            print('Defaulting to select out-of-bag sample for most recent year.')
            oob_year = original_frame.Year.unique().max()

        # slice get dataframe for that year
        oob_data = original_frame[original_frame.Year == oob_year]

        return oob_data

    @classmethod
    def oob_train_split(cls, full_data, test_data):
        """
        Function that takes the generated out of bag frame and creates a training dataset
        from full data by removing oob data

        Input:
            full_data = Pandas dataframe of crime counts from Initialiser
            test_data = Pandas dataframe output from out_of_bag_prep (holdout year data)

        Output:
            train_data = Pandas dataframe of crime counts that are not in test_data
        """

        oob_year = test_data.Year.unique().max()

        original_frame = full_data

        # define data for modelling that removes year being modelled
        train_data = original_frame[(original_frame.Year != oob_year)]

        return train_data

    @classmethod
    def SimplePoission(cls, train_data, test_data):
        """
        Function for generating synthetic crime count data at LSOA at timescale resolution
        based on historic data loaded from the initialiser.

        Inputs:
            train_data = Pandas dataframe output from oob_train_split
            test_data = Pandas dataframe output from out_of_bag_prep

        Output:
            simulated_year_frame = Pandas dataframe of simulated data based on train_data
                                   to be compared to test_data

        Notes:
            Could this be performed before the psuedo day/week allocation?
        """

        # building a model that incorporates these local populations
        year = test_data.Year.unique().max()

        oob_data = test_data

        historic_data = train_data

        # test if psuedo-Weeks have been allocated
        if 'Week' in historic_data.columns:
            time_res = 'Week'
        else:
            time_res = 'Day'


        # a list for all rows of data frame produced
        print('Beginning sampling.')

        time_lbl = []
        mon_lbl = []
        crime_lbl = []
        count_lbl = []
        LSOA_lbl = []

        crime_types_lst = historic_data['Crime_type'].unique()

        # for each month in the range of months in oob data
        for mon in range(oob_data.Mon.unique().min(), (oob_data.Mon.unique().max() + 1)):

            # use week range for oob year
            accepted_wk_range = oob_data[(oob_data.Year.values == year) & (oob_data.Mon.values == mon)][time_res].unique()

            # for each week
            for wk in np.sort(accepted_wk_range):

                print('Month: '+str(mon)+' '+time_res+': '+str(wk))


                # for each crime type
                for crim_typ in crime_types_lst:

                    frame_OI = historic_data[(historic_data['Mon'].isin([mon])) &
                                             (historic_data[time_res].isin([wk])) &
                                             (historic_data['Crime_type'].isin([crim_typ]))]

                    for LSOA in frame_OI['LSOA_code'].unique():

                        frame_OI2 = frame_OI[(frame_OI['LSOA_code'].isin([LSOA]))]

                        if len(frame_OI2) > 0:

                            # create a normal distribution of crime counts on the given day in a given month and randomly select a count number (round it to integer)
                            # if standard deviation is nan set value for that day at 0
                            sim_count = scipy.stats.poisson(round(frame_OI2['Counts'].mean(), 0)).rvs()

                            # append values to lists that will be merged into dict in final step
                            time_lbl.append(wk)
                            mon_lbl.append(mon)
                            crime_lbl.append(crim_typ)
                            count_lbl.append(sim_count)
                            LSOA_lbl.append(LSOA)

        # concatenate all these compiled dataframe rows into one large dataframe
        simulated_year_frame = pd.DataFrame.from_dict({time_res : time_lbl,
                                                       'Mon' : mon_lbl,
                                                       'Crime_type' : crime_lbl,
                                                       'Counts' : count_lbl,
                                                       'LSOA_code' : LSOA_lbl})


        return simulated_year_frame


    @classmethod
    def error_Reporting(cls, test_data, simulated_data):
        """
        function for building comparison of simulated dataframe to actual out-of-bag frame

        Inputs:
            test_data = Pandas dataframe output from out_of_bag_prep
            simulated_year_frame = Pandas dataframe output from SimplePoission of simulated year crime counts

        Outputs:
            comparison_frame = Pandas dataframe that shows comparison of simulated data to test_data
                               with error scores printed and plot
        """

        # test for days or Weeks
        # TODO: improve this somehow??
        # specify value as class attribute earlier?
        if 'Week' in simulated_data.columns:
            time_res = 'Week'
        else:
            time_res = 'Day'

        comparison_frame = pd.concat([simulated_data.groupby([time_res,'LSOA_code'])['Counts'].sum(), test_data.groupby([time_res,'LSOA_code'])['Counts'].sum()],axis=1)

        comparison_frame.reset_index(time_res, inplace=True)

        comparison_frame.columns = [time_res,'Pred_counts','Actual']

        comparison_frame['Difference'] = abs(comparison_frame.Pred_counts - comparison_frame.Actual)

        y_rmse = np.sqrt(mean_squared_error(comparison_frame.Actual, comparison_frame.Pred_counts))

        y_ame = mean_absolute_error(comparison_frame.Actual, comparison_frame.Pred_counts)

        y_medae = median_absolute_error(comparison_frame.Actual, comparison_frame.Pred_counts)

        print('Root mean squared error of poisson sampler: ',round(y_rmse, 1))

        print('Mean absolute error: ', round(y_ame, 1))

        print('Median absolute error: ', round(y_medae, 1))

        comparison_frame[['Pred_counts','Actual']].plot.scatter(x='Actual',y='Pred_counts')
        plt.plot([0,175],[0,175], 'k--')

        plt.show()

        return comparison_frame
