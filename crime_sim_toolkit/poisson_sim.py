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

    def __init__(self, LA_names):

        self.data = Initialiser().get_data(LA_names=LA_names)

    def out_of_bag_prep(self):
        """
        Function for selecting out a year of real data from counts data for
        out-of-bag sampler comparison
        """

        original_frame = self.data

        # identify highest year with complete counts for entire year
        # this will be used as out-of-bag comparator
        try:
            oob_year = original_frame.Year.unique()[original_frame.groupby('Year')['Mon'].unique().map(lambda x: len(x) == 12)].max()

        except ValueError:
            print('The passed data does not appear to have a full years (Jan-Dec) worth of data.')
            print('Defaulting to select out-of-bag sample for most recent year.')
            oob_year = original_frame.Year.unique().max()

        # slice get dataframe for that year
        self.oob_data = original_frame[original_frame.Year == oob_year]

        return self.oob_data

    def oob_train_split(self):
        """
        Function that takes the generated out of bag frame and creates a training dataset
        from full data by removing oob data
        """

        oob_year = self.oob_data.Year.unique().max()

        original_frame = self.data

        # define data for modelling that removes year being modelled
        train_data = original_frame[(original_frame.Year != oob_year)]

        return train_data


    def SimplePoission(self):
        """
        Function for generating synthetic crime count data at LSOA at timescale resolution
        based on historic data loaded from the initialiser.
        """

        # initialise oob data

        self.out_of_bag_prep()

        # building a model that incorporates these local populations

        year = self.oob_data.Year.unique().max()

        oob_data = self.oob_data

        historic_data = self.oob_train_split()

        # test if psuedo-Weeks have been allocated
        if 'Week' in historic_data.columns:
            time_res = 'Week'
        else:
            time_res = 'Day'


        # a list for all rows of data frame produced
        print('Beginning sampling.')

        frames_pile = []

        # for each month in the range of months in oob data
        for mon in range(oob_data.Mon.unique().min(), (oob_data.Mon.unique().max() + 1)):

            # use week range for oob year
            accepted_wk_range = oob_data[(oob_data.Year == year) & (oob_data.Mon == mon)][time_res].unique()

            # for each week
            for wk in accepted_wk_range:

                print('Month :'+str(mon)+' '+time_res+': '+str(wk))

                # for each crime type
                for crim_typ in historic_data['Crime_type'].unique():

                    frame_OI = historic_data[(historic_data['Mon'] == mon) &
                                            (historic_data[time_res] == wk) &
                                            (historic_data['Crime_type'] == crim_typ)]

                    for LSOA in frame_OI['LSOA_code'].unique():

                        frame_OI2 = frame_OI[(frame_OI['LSOA_code'] == LSOA)]

                        if len(frame_OI2) > 0:

                            # calculate the mean total count of that crime type for the given day on the given month
                            # using built in mean calculation will not take into account years without crime as they do not feature as a 0
                            day_mean = round(frame_OI2['Counts'].mean(), 0)


                            # create a normal distribution of crime counts on the given day in a given month and randomly select a count number (round it to integer)
                            # if standard deviation is nan set value for that day at 0
                            sim_count = scipy.stats.poisson(day_mean).rvs()

                            # create a dictionary for the row of data corresponding to simulated crime counts for the given day in a given month for a given crime type
                            crime_count = {time_res : [wk],
                                           'Mon' : [mon],
                                           'Crime type' : [crim_typ],
                                           'Count' : [sim_count],
                                           'LSOA_code' : [LSOA]}

                            # create a dataframe from the above dict
                            frame_line1 = pd.DataFrame.from_dict(crime_count)

                            # append this dataframe (1 line) to the frames_pile
                            frames_pile.append(frame_line1)


        # concatenate all these compiled dataframe rows into one large dataframe
        simulated_year_frame = pd.concat(frames_pile, axis=0)

        # reset the index
        simulated_year_frame.reset_index(inplace=True, drop=True)

        return simulated_year_frame


    def figure_comparison(self, simulated_data):
        """
        Function for plotting simulated v real data
        TODO: is this function necessary?
        """

        oob_data = self.oob_data

        plt.figure(figsize=(16,10))
        plt.subplot(2,2,1)
        simulated_data.Count.value_counts().plot.bar()
        plt.title('Simulated years count distribution')

        plt.subplot(2,2,2)
        oob_data[(oob_data.Year == 2018)].Counts.value_counts().plot.bar()
        plt.title('Count distribution for 2018')

        plt.figure(figsize=(16,10))
        plt.subplot(2,2,1)
        simulated_data.groupby(['Mon','Week'])['Count'].sum().plot()
        plt.title('Simulated counts per week')

        plt.subplot(2,2,2)
        oob_data[(oob_data.Year == 2018)].groupby(['Mon','Week'])['Counts'].sum().plot()
        plt.title('Counts per week for 2018')

        return plt.show()


    def error_Reporting(self, simulated_data):
        """
        function for building comparison of simulated dataframe to actual out-of-bag frame
        """

        # test for days or Weeks
        # TODO: improve this somehow??
        # specify value as class attribute earlier?
        if 'Week' in simulated_data.columns:
            time_res = 'Week'
        else:
            time_res = 'Day'

        comparison_frame = pd.concat([simulated_data.groupby([time_res,'LSOA_code'])['Count'].sum(), self.oob_data.groupby([time_res,'LSOA_code'])['Counts'].sum()],axis=1)

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
