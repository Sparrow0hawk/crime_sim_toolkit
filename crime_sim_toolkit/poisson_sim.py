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
from crime_sim_toolkit import utils


class Poisson_sim:
    """
    Functionality for building simple poisson sampling crime data generator
    Requires data from https://data.police.uk/ in data folder
    """

    def __init__(self, LA_names, directory=None, timeframe='Week', aggregate=False):

        self.data = Initialiser(LA_names=LA_names).get_data(directory=directory,
                                                            timeframe=timeframe,
                                                            aggregate=aggregate)

    @classmethod
    def out_of_bag_prep(cls, full_data):
        """
        Function for selecting out a year of real data from counts data for
        out-of-bag sampler comparison

        Input: Pandas dataframe of crime counts in format from initialiser | can pass class instance

        Output: Pandas dataframe of crime counts for maximum year in dataset to be held as out of bag test set
        """

        original_frame = utils.validate_datetime(full_data)

        # identify highest year with complete counts for entire year
        oob_year = original_frame.datetime.max().year

        # slice get dataframe for that year
        oob_data = original_frame[original_frame.datetime.dt.year == oob_year]

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

        # ensure datetime is configured to datetime dtype
        test_data = utils.validate_datetime(test_data)


        oob_year = test_data.datetime.max().year

        # ensure datetime is configured to datetime dtype
        original_frame = utils.validate_datetime(full_data)

        # define data for modelling that removes year being modelled
        train_data = original_frame[(original_frame.datetime.dt.year != oob_year)]

        return train_data

    @classmethod
    def SimplePoission(cls, train_data, test_data, method='simple', mv_window=0):
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

        # validate datetime columns within input data
        oob_data = utils.validate_datetime(test_data.copy())

        historic_data = utils.validate_datetime(train_data.copy())

        # method dict for sampling approaches
        # simple : fits a poisson based on all data passed
        # mixed : fits a poisson and linear model and calulates mean counts from both models
        # mw : moving-window model that fits a poisson from crime counts for +/- 1 day
        # zero : drops zeroes before fitting poisson unless all zero

        methods_dict = {'simple' : cls.simple_sampler,
                        'mixed' : cls.mixed_sampler,
                        'zero' : cls.zero_sampler}

        # test if psuedo-Weeks have been allocated
        if 'Week' in historic_data.columns:
            time_res = 'Week'

            # select the year from the oob_data
            year = oob_data.datetime.max().year
        else:
            time_res = 'datetime'

        print('Time resolution set to: ', time_res)

        # a list for all rows of data frame produced
        print('Beginning sampling.')

        time_lbl = []
        mon_lbl = []
        crime_lbl = []
        count_lbl = []
        LSOA_lbl = []

        crime_types_lst = historic_data['Crime_type'].unique()

        # for each month in the range of months in oob data
        for date in np.sort(np.unique(oob_data[time_res].tolist())):

            print('Simulating '+time_res+': '+str(date))

            # create a loop for creating a date list based on
            # moving window arguement
            if time_res != 'Week':

                date_lst = []

                date_lst += cls.moving_window_datetime(datetime=date,
                                                   window=mv_window)

            # for each crime type
            for crim_typ in crime_types_lst:

                # include if-else block to catch different handling of week/day
                if time_res == 'Week':

                    # moving window for weeks
                    date_lst = []

                    date_lst += cls.moving_window_week(week=date,
                                                   window=mv_window)


                    frame_OI = historic_data[(historic_data[time_res].isin([week for week in date_lst])) &
                                             (historic_data['Crime_type'].isin([crim_typ]))]

                else:
                    frame_OI = historic_data[(historic_data[time_res].dt.day.isin([date.day for date in date_lst])) &
                                             (historic_data[time_res].dt.month.isin([date.month for date in date_lst])) &
                                             (historic_data['Crime_type'].isin([crim_typ]))]

                for LSOA in frame_OI['LSOA_code'].unique():

                    frame_OI2 = frame_OI[(frame_OI['LSOA_code'].isin([LSOA]))]

                    if len(frame_OI2) > 0:

                        # append values to lists that will be merged into dict in final step
                        time_lbl.append(date)
                        # section to capture datetime for week sim
                        if time_res == 'Week':

                            mon_lbl.append(str(year) + '-' + str(frame_OI2.datetime.dt.month.tolist()[0]))

                        crime_lbl.append(crim_typ)
                        count_lbl.append(methods_dict[method](narrow_frame=frame_OI2))
                        LSOA_lbl.append(LSOA)

                    # need else catch here incase data is missing
                    # becase order of lists is messed up if absent
                    elif len(frame_OI2) == 0:

                        # append values to lists that will be merged into dict in final step
                        time_lbl.append(date)
                        # section to capture datetime for week sim
                        if time_res == 'Week':

                            mon_lbl.append(str(year) + '-' + str(frame_OI2.datetime.dt.month.tolist()[0]))

                        crime_lbl.append(crim_typ)
                        count_lbl.append(0)
                        LSOA_lbl.append(LSOA)

        if time_res == 'Week':

            results_dict = {time_res : time_lbl,
                         'datetime' : mon_lbl,
                         'Crime_type' : crime_lbl,
                         'Counts' : count_lbl,
                         'LSOA_code' : LSOA_lbl}
        else:

            results_dict = {time_res : time_lbl,
                         'Crime_type' : crime_lbl,
                         'Counts' : count_lbl,
                         'LSOA_code' : LSOA_lbl}

        # concatenate all these compiled dataframe rows into one large dataframe
        simulated_year_frame = pd.DataFrame.from_dict(results_dict)


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


        test_data = utils.validate_datetime(test_data)

        simulated_data = utils.validate_datetime(simulated_data)
        # test for days or Weeks
        # TODO: improve this somehow??
        # specify value as class attribute earlier?
        if 'Week' in simulated_data.columns:
            time_res = 'Week'
        else:
            time_res = 'datetime'

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
            print('Oversampling by: ', 100 *((round(comparison_frame.Pred_counts.sum() / comparison_frame.Actual.sum(), 3) - 1)), '%')
        else:
            print('Undersampling by: ', 100 *((round(comparison_frame.Pred_counts.sum() / comparison_frame.Actual.sum(), 3)) - 1), '%')
        print('-------')

        comparison_frame[['Pred_counts','Actual']].plot.scatter(x='Actual',y='Pred_counts')
        plt.plot([0,comparison_frame[['Pred_counts','Actual']].max().max() + 25 ],[0,comparison_frame[['Pred_counts','Actual']].max().max() + 25 ], 'k--')

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
            # TODO: correct this to account for new datetime column
            x_Years = narrow_frame['datetime'].dt.year.values.reshape(-1, 1)

            # get counts as the Y variable
            y_Counts = narrow_frame['Counts'].values

            # fit the model based on data
            model = linReg().fit(x_Years, y_Counts)

            # predict the counts for the next year
            lin_count = round(model.predict(np.array([x_Years[-1] + 1])).item(),0)

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

    @staticmethod
    def moving_window_week(week, window=0):
        """
        Simple method for getting week numbers adjacent to
        a given week value
        """

        # get list of week numbers
        week_lst = [x for x in range(1,53)]

        # get the index of given week
        date_idx = week_lst.index(week)

        window_lst = [week]

        for win in range(1, window+1):

            # get the index ahead
            jInd = (date_idx - win) % len(week_lst)

            kInd = (date_idx + win) % len(week_lst)

            window_lst.append(week_lst[jInd])

            window_lst.append(week_lst[kInd])

        return window_lst

    @staticmethod
    def moving_window_datetime(datetime, window=0):
        """
        Simple method for getting week numbers adjacent to
        a given week value
        """

        window_lst = [datetime]

        for window in range(1,window+1):

            window_lst.append(datetime + pd.DateOffset(days=window))

            window_lst.append(datetime - pd.DateOffset(days=window))

        return window_lst
