"""
Utility functions for general use
"""

import pandas as pd
import numpy as np

def counts_to_reports(counts_frame):
    """
    Function for converting Pandas dataframes of aggregated crime counts per timeframe (day/week)
    per LSOA per crime type into a pandas dataframe of individual reports
    """

    pri_data = counts_frame

    if 'Week' in pri_data.columns:
        time_res = 'Week'
    else:
        time_res = 'Day'

    # first drop all instances where Counts == 0

    pri_data = pri_data[pri_data.Counts != 0]

    # generate a randomly allocated unique crime number
    # allocated per loop or cumulatively at the end based on final len?
    # take a row with count value > 0 return number of new rows with details as count value

    # empty list for rows to be added to for eventual concatenation
    concat_stack = []
    UID_col = []

    for idx, row in pri_data.iterrows():

        for count in range(row.Counts):

            concat_stack.append(row.loc[[time_res,'Mon','Crime_type','LSOA_code']].values)

            UID = str(row['LSOA_code'][:5]) + str(row[time_res]) + str(row['Mon']) + str(row['Crime_type'][0]) + str(count)

            UID_col.append(UID)



    reports_frame = pd.DataFrame(data=np.stack(concat_stack),
                 index=range(len(concat_stack)),
                 columns=[time_res,'Mon','Crime_type','LSOA_code']
                 )

    # create unique IDs from fragments of data
    reports_frame['UID'] = UID_col

    return reports_frame

def populate_offense(crime_frame):
    """
    Function for adding in more specific offense descriptions based on Police
    Recorded Crime Data tables.
    """

    return populated_frame
