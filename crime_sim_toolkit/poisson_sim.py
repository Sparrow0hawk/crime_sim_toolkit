# TODO: this section will simply be for the poisson sampler code
# it will call out to a separate initialiser function to actually get data

# import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from sklearn.metrics import mean_squared_error, median_absolute_error, mean_absolute_error


class Poisson_sim:
    """
    Functionality for building simple poisson sampling crime data generator
    Requires data from https://data.police.uk/ in data folder
    """

    def __init__(self):
        pass


    def out_of_bag_prep(self):
        """
        Function for selecting out a year of real data from counts data for
        out-of-bag sampler comparison
        """

        oob_crime_counts = new_tot_counts[(new_tot_counts.Year != 2018) & (new_tot_counts.Year != 2019)]


    def SimplePoission(self):

        # building a model that incorporates these local populations
        # performs out-of-bag sampling for 2018

        # a list for all rows of data frame produced
        frames_pile = []

        # for each month in 12 months
        for mon in range(1,13):

            # use week range for 2018 for comparison
            accepted_wk_range = new_tot_counts[(new_tot_counts.Year == 2018) & (new_tot_counts.Mon == mon)].Week.unique()

            # for each week
            for wk in accepted_wk_range:

                print('Month :'+str(mon)+' Week: '+str(wk))

                # for each crime type

                for crim_typ in oob_crime_counts['Crime_type'].unique():

                    frame_OI = oob_crime_counts[(oob_crime_counts['Mon'] == mon) &
                                            (oob_crime_counts['Week'] == wk) &
                                            (oob_crime_counts['Crime_type'] == crim_typ)]

                    for LSOA in frame_OI['LSOA_code'].unique():

                        frame_OI2 = frame_OI[(frame_OI['LSOA_code'] == LSOA)]

                        if len(frame_OI2) > 0:

                            # calculate the mean total count of that crime type for the given day on the given month
                            # using built in mean calculation will not take into account years without crime as they do not feature as a 0
                            day_mean = round(frame_OI2['Counts'].mean(), 0)


                            # create a normal distribution of crime counts on the given day in a given month and randomly select a count number (round it to integer)
                            # if standard deviation is nan set value for that day at 0

                            sim_count = scipy.stats.poisson(day_mean).rvs()

                              # if check to ensure number is not negative

                            # create a dictionary for the row of data corresponding to simulated crime counts for the given day in a given month for a given crime type
                            crime_count = {'Week' : [wk],
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


# this takes a very long time, quite a lot of dimensions going on.
    def figure_comparison(self):
        """
        Function for plotting simulated v real data
        TODO: is this function necessary?
        """

        plt.figure(figsize=(16,10))
        plt.subplot(2,2,1)
        simulated_year_frame.Count.value_counts().plot.bar()
        plt.title('Simulated years count distribution')

        plt.subplot(2,2,2)
        new_tot_counts[(new_tot_counts.Year == 2018)].Counts.value_counts().plot.bar()
        plt.title('Count distribution for 2018')

        plt.figure(figsize=(16,10))
        plt.subplot(2,2,1)
        simulated_year_frame.groupby(['Mon','Week'])['Count'].sum().plot()
        plt.title('Simulated counts per week')

        plt.subplot(2,2,2)
        new_tot_counts[(new_tot_counts.Year == 2018)].groupby(['Mon','Week'])['Counts'].sum().plot()
        plt.title('Counts per week for 2018')

    def error_Reporting(self):
        """
        function for building comparison of simulated dataframe to actual out-of-bag frame
        """

        comparison_frame = pd.concat([simulated_year_frame.groupby(['Week','LSOA_code'])['Count'].sum(), new_tot_counts[new_tot_counts.Year == 2018].groupby(['Week','LSOA_code'])['Counts'].sum()],axis=1)

        comparison_frame.reset_index('Week', inplace=True)

        comparison_frame.columns = ['Week','Pred_counts','Actual']

        comparison_frame.head()

        comparison_frame['Difference'] = abs(comparison_frame.Pred_counts - comparison_frame.Actual)

        y_rmse = np.sqrt(mean_squared_error(comparison_frame.Actual, comparison_frame.Pred_counts))

        y_ame = mean_absolute_error(comparison_frame.Actual, comparison_frame.Pred_counts)

        y_medae = median_absolute_error(comparison_frame.Actual, comparison_frame.Pred_counts)

        print('Root mean squared error of poisson sampler: ',round(y_rmse, 1))

        print('Mean absolute error: ', round(y_ame, 1))

        print('Median absolute error: ', round(y_medae, 1))

        comparison_frame['Difference'].sum() / len(comparison_frame)

        comparison_frame[['Pred_counts','Actual']].plot.scatter(x='Actual',y='Pred_counts')
        plt.plot([0,175],[0,175], 'k--')
