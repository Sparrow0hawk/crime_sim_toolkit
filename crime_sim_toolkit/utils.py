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

    pri_data = validate_datetime(counts_frame)

    if 'Week' in pri_data.columns:
        time_res = 'Week'
    else:
        time_res = 'datetime'

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

            if time_res == 'Week':

                concat_stack.append(row.loc[['datetime',time_res,'Crime_type','LSOA_code']].values)

                col_names = ['datetime',time_res,'Crime_type','LSOA_code']

                UID = str(row['LSOA_code'][:5]).strip() +\
                      str(row['datetime'].day).strip() +\
                      str(row['datetime'].month).strip() +\
                      str(row['Crime_type'][:2]).strip().upper() +\
                      str(count).strip()

                UID_col.append(UID)

            else:

                concat_stack.append(row.loc[['datetime','Crime_type','LSOA_code']].values)

                col_names = ['datetime','Crime_type','LSOA_code']

                UID = str(row['LSOA_code'][:5]).strip() +\
                      str(row['datetime'].day).strip() +\
                      str(row['datetime'].month).strip() +\
                      str(row['Crime_type'][:2]).strip().upper() +\
                      str(count).strip()

                UID_col.append(UID)


    reports_frame = pd.DataFrame(data=np.stack(concat_stack),
                 index=range(len(concat_stack)),
                 columns=col_names
                 )

    # create unique IDs from fragments of data
    reports_frame['UID'] = UID_col

    # reorder columns for ABM
    reports_frame = reports_frame[['UID'] + col_names]

    return reports_frame

def populate_offence(crime_frame):
    """
    Function for adding in more specific offense descriptions based on Police
    Recorded Crime Data tables.

    Profiled run on test data:
    # ver2
    CPU times: user 2min 19s, sys: 2.09 s, total: 2min 21s
    Wall time: 2min 21s
    """

    # format columns to remove spaces
    crime_frame.columns = crime_frame.columns.str.replace(' ','_')

    if 'Week' in crime_frame.columns:
        time_res = 'Week'
    else:
        time_res = 'datetime'

    # initially load reference tables
    LSOA_pf_reference = pd.read_csv(pkg_resources.resource_filename(resource_package, 'src/LSOA_data/PoliceforceLSOA.csv'),
                                    index_col=0)

    descriptions_reference = pd.read_csv(pkg_resources.resource_filename(resource_package, 'src/prc-pfa-201718_new.csv'),
                             index_col=0)

    # test if the first instance in LSOA code is within police force frame?
    # if value is not in the list of police forces from reference frame
    # add police force column
    if crime_frame['LSOA_code'].unique().tolist()[0] not in LSOA_pf_reference.Police_force.tolist():

        crime_frame['Police_force'] = crime_frame.LSOA_code.map(lambda x: LSOA_pf_reference[LSOA_pf_reference['LSOA Code'].isin([x])].Police_force.tolist()[0])

    # else convert LSOA_code to Police_force column
    else:

        crime_frame['Police_force'] = crime_frame['LSOA_code']

    list_of_slices = []

    for police_force in crime_frame.Police_force.unique():

        shortened_frame = crime_frame[crime_frame['Police_force'] == police_force].copy()

        # create sliced frame of crime descriptions by police force
        descriptions_slice = descriptions_reference[descriptions_reference['Force_Name'].isin([police_force])]

        # create pivot table for random allocating weighting
        pivoted_slice = ((descriptions_slice.groupby(['Policeuk_Cat','Offence_Group','Offence_Description'])['Number_of_Offences'].sum() \
        / descriptions_slice.groupby(['Policeuk_Cat'])['Number_of_Offences'].sum())).reset_index()

        shortened_frame['Crime_description'] = shortened_frame['Crime_type'].map(lambda x: np.random.choice(pivoted_slice[pivoted_slice.Policeuk_Cat.str.lower().isin([x.lower()])].Offence_Description.tolist(), 1, p = pivoted_slice[pivoted_slice.Policeuk_Cat.str.lower().isin([x.lower()])].Number_of_Offences.tolist())[0] if len(pivoted_slice[pivoted_slice.Policeuk_Cat.str.lower().isin([x.lower()])]) > 0 else x)

        list_of_slices.append(shortened_frame)

    populated_frame = pd.concat(list_of_slices)

    # reorder columns for ABM

    if time_res == 'Week':

        populated_frame = populated_frame[['UID','datetime',time_res,'Crime_description','Crime_type','LSOA_code','Police_force']]

    else:

        populated_frame = populated_frame[['UID','datetime','Crime_description','Crime_type','LSOA_code','Police_force']]

    return populated_frame

def validate_datetime(passed_dataframe):
    """
    Utility function to ensure passed dataframes datetime column is configured as
    datetime dtype.
    """

    if np.dtype('datetime64[ns]') not in passed_dataframe.dtypes:

        try:
            passed_dataframe['datetime'] = passed_dataframe['datetime'].apply(lambda x: pd.to_datetime(x))

            print('Datetime column configured.')

        except:
            print('No datetime column detected. Dataframe unaltered.')

    validated_date_frame = passed_dataframe.copy()

    return validated_date_frame
