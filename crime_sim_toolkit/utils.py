"""
Utility functions for general use
"""

import pandas as pd
import numpy as np
import pkg_resources

resource_package = 'crime_sim_toolkit'

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

def populate_offence(crime_frame):
    """
    Function for adding in more specific offense descriptions based on Police
    Recorded Crime Data tables.

    Profiled run on test data:
    # ver1
    CPU times: user 6min 10s, sys: 710 ms, total: 6min 11s
    Wall time: 6min 13s
    """

    # format columns to remove spaces
    crime_frame.columns = crime_frame.columns.str.replace(' ','_')

    # initially load reference tables
    LSOA_pf_reference = pd.read_csv(pkg_resources.resource_filename(resource_package, 'src/LSOA_data/PoliceforceLSOA.csv'),
                                    index_col=0)

    descriptions_reference = pd.read_csv(pkg_resources.resource_filename(resource_package, 'src/prc-pfa-201718_new.csv'),
                             index_col=0)

    # first identify police force
    list_of_descriptions = []

    for index, row in crime_frame.iterrows():

        police_force = LSOA_pf_reference[LSOA_pf_reference['LSOA Code'].isin([row.LSOA_code])].Police_force.tolist()[0]

        descriptions_slice = descriptions_reference[descriptions_reference['Force_Name'].isin([police_force])]

        pivoted_slice = ((descriptions_slice.groupby(['Policeuk_Cat','Offence_Group','Offence_Description'])['Number_of_Offences'].sum() \
        / descriptions_slice.groupby(['Policeuk_Cat'])['Number_of_Offences'].sum())).reset_index()

        example_narrow = pivoted_slice[pivoted_slice.Policeuk_Cat.str.lower().isin([row['Crime_type'].lower()])]

        if len(example_narrow) > 0:

            list_of_descriptions.append(np.random.choice(example_narrow.Offence_Description.tolist(), 1, p=example_narrow.Number_of_Offences)[0])

        else:
            # this will prevent an error on anti-social behaviour which is not included
            # within mapping file
            list_of_descriptions.append(row['Crime_type'])

    populated_frame = crime_frame.copy()

    populated_frame['Crime_description'] = list_of_descriptions

    return populated_frame
