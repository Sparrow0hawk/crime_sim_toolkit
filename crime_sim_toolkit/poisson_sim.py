# TODO: this section will simply be for the poisson sampler code
# it will call out to a separate initialiser function to actually get data

# import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from sklearn.linear_model import LinearRegression as linReg
from sklearn.metrics import mean_squared_error, median_absolute_error, mean_absolute_error
from crime_sim_toolkit.initialiser import Initialiser


class Poisson_sim:
    """
    Functionality for building simple poisson sampling crime data generator
    Requires data from https://data.police.uk/ in data folder
    """

    def __init__(self, LA_names, directory=None, timeframe='Week'):

        self.data = Initialiser(LA_names=LA_names).get_data(directory=directory, timeframe=timeframe)

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
    def SimplePoission(cls, train_data, test_data, method='simple'):
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

        # method dict for sampling approaches
        # simple : fits a poisson based on all data passed
        # mixed : fits a poisson and linear model and calulates mean counts from both models
        # mw : moving-window model that fits a poisson from crime counts for +/- 1 day
        # zero : drops zeroes before fitting poisson unless all zero

        methods_dict = {'simple' : cls.simple_sampler,
                        'mixed' : cls.mixed_sampler,
                        'mw' : cls.moving_window,
                        'zero' : cls.zero_sampler}

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

                            sim_count = methods_dict[method](narrow_frame=frame_OI2)

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

        # set simulated data to return the year data is simulated for
        simulated_year_frame['Year'] = year


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

        # new section that prints cumulative over/undersampling
        # perhaps more useful metric eval
        print('-----------')
        print('Total simulated crime events: ', comparison_frame.Pred_counts.sum())
        print('Total crime events in holdout data: ', comparison_frame.Actual.sum())

        if (comparison_frame.Pred_counts.sum() - comparison_frame.Actual.sum()) > 0:
            print('Oversampling by: ', 100 *((round(comparison_frame.Pred_counts.sum() / comparison_frame.Actual.sum(), 1) - 1)), '%')
        else:
            print('Undersampling by: ', 100 *((round(comparison_frame.Pred_counts.sum() / comparison_frame.Actual.sum(), 1)) - 1), '%')
        print('-------')

        comparison_frame[['Pred_counts','Actual']].plot.scatter(x='Actual',y='Pred_counts')
        plt.plot([0,175],[0,175], 'k--')

        plt.show()

        return comparison_frame

    @classmethod
    def simple_sampler(cls, narrow_frame):
            """
            Simple function for data sampler
            """
            sim_count = scipy.stats.poisson(round(narrow_frame['Counts'].mean(), 0)).rvs()

            return sim_count

    @classmethod
    def mixed_sampler(cls, narrow_frame):
            """
            A mixed sampling method
            It both randomly samples from a poisson model and fits a linear model
            from count data and determines the mean of those values
            """

            # randomly sample from a fitted poisson model
            poi_count = scipy.stats.poisson(round(narrow_frame['Counts'].mean(), 0)).rvs()

            # prep data for linear model

            # get years as the X variable
            x_Years = narrow_frame['Year'].values.reshape(-1, 1)

            # get counts as the Y variable
            y_Counts = narrow_frame['Counts'].values

            # fit the model based on data
            model = linReg().fit(x_Years, y_Counts)

            # predict the counts for the next year
            lin_count = round(np.asscalar(model.predict(np.array([x_Years[-1] + 1]))),0)

            # calculate the mean of linear and poisson counts
            mixed_val = round(np.mean([lin_count, poi_count]), 0)

            return mixed_val

    @classmethod
    def zero_sampler(cls, narrow_frame):
            """
            A sampling method that removes zero counts from count dataframe
            """
            # remove zeroes or if all zeroes set to zero

            if narrow_frame['Counts'].mean() == 0:

                sim_count = 0

            else:
                narrow_frame = narrow_frame[narrow_frame['Counts'] != 0]

                # create a normal distribution of crime counts on the given day in a given month
                #and randomly select a count number (round it to integer)
                # if standard deviation is nan set value for that day at 0
                sim_count = scipy.stats.poisson(round(narrow_frame['Counts'].mean(), 0)).rvs()

            return sim_count

    @classmethod
    def moving_window(cls, narrow_frame):
            """
            A moving window sampler function
            TODO: this actually requires quite a significant refactor
            As other functions are able to take reduced dataframe whereas this will
            change behaviours in loops above.
            """

            return
