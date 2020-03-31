"""
Utility script for wrangling data for use in the Microsimulator class of
crime_sim_toolkit

Required for data from data.police.uk/ to add more specific crime classification
(based on regional levels) and to allocate victim demographic data (infered from
census data)
"""
import numpy as np
import pandas as pd
import glob
import pkg_resources

def main():

    load_pop(2017).to_csv('/content/WY_pop_2017.csv', index=False)

    load_pop(2018).to_csv('/content/WY_pop_2018.csv', index=False)

    # we'll use this crime dataframe to add demographic data
    big_crime_data = load_and_squash('/content/wyp_data_2017')


    pop_2017 = load_pop(2017)

    pop_2017['multi_cat_col'] = pop_2017.DC1117EW_C_SEX.astype(str) \
                                + '-' + pop_2017.DC1117EW_C_AGE.astype(str) \
                                + '-' + pop_2017.DC2101EW_C_ETHPUK11.astype(str)

    demographic_prop = pop_2017['multi_cat_col'].value_counts() / pop_2017['multi_cat_col'].value_counts().sum()

    big_crime_data['victim_profile'] = big_crime_data\
    .apply(lambda x: np.random.choice(demographic_prop.index, p=demographic_prop.values), axis=1)

    # we now need to split the victim_profile column (as we don't actually expect data to look like this)

    expanded_demo = big_crime_data['victim_profile'].str.split('-', expand=True)

    expanded_demo.columns = ['sex','age','ethnicity']

    big_crime_data = pd.concat([big_crime_data, expanded_demo], axis=1)

    # we will also now drop lines with NaN in LSOA_code columns
    big_crime_data = big_crime_data.dropna(subset=['LSOA code'])

    big_crime_data = populate_offence(big_crime_data)

    big_crime_data.to_csv('/content/wyp_crime_2017.csv', index=False)

######### utility functions ############

def load_and_squash(directory : str):
  """
  A function for loading multiple csv files and squashing them into one
  """

  if directory[-1] != '/':

    directory += '/'

  list_of_files = glob.glob(directory+'*')

  list_of_df = []

  for file in list_of_files:

    list_of_df.append(pd.read_csv(file))

  return pd.concat(list_of_df)


def load_pop(year=2017):

    file_list = glob.glob('/content/WY_spenser_dat_small/*')

    year_str = str(year)

    selected_files = [file for file in file_list if year_str in file]

    print('Number of files found: ',len(selected_files))

    files_combo = []

    for file in selected_files:

            open_file = pd.read_csv(file)

            files_combo.append(open_file)

    combined_files = pd.concat(files_combo, axis=0)

    combined_files.reset_index(inplace=True, drop=True)

    return combined_files


def populate_offence(crime_frame):
    """
    Function for adding in more specific offense descriptions based on Police
    Recorded Crime Data tables.

    Profiled run on test data:
    # ver2
    CPU times: user 2min 19s, sys: 2.09 s, total: 2min 21s
    Wall time: 2min 21s
    """

    resource_package = 'crime_sim_toolkit'

    # format columns to remove spaces
    crime_frame.columns = crime_frame.columns.str.replace(' ','_')

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

    # for each police force within the passed crime reports data frame
    print(crime_frame.Police_force.unique())

    for police_force in crime_frame.Police_force.unique():

        # slice a frame for data in a specific police force
        shortened_frame = crime_frame[crime_frame['Police_force'] == police_force].copy()

        # create sliced frame of crime description proportions by police force
        descriptions_slice = descriptions_reference[descriptions_reference['Force_Name'].isin([police_force])]

        # create pivot table for random allocating weighting
        # this creates a table of offence description percentages for each Policeuk_Cat
        pivoted_slice = ((descriptions_slice.groupby(['Policeuk_Cat','Offence_Group','Offence_Description'])['Number_of_Offences'].sum() \
        / descriptions_slice.groupby(['Policeuk_Cat'])['Number_of_Offences'].sum())).reset_index()

        # add a Crime_description column that is generated by taking each Crime_type (Policeuk_cat)
        # and using np.random.choice to randomly allocate a Crime description for the given Crime_type
        # weighted by the percentages in the pivot table created above
        shortened_frame['Crime_description'] = shortened_frame['Crime_type'].map(lambda x: np.random.choice(
                                                                                 # specify list of choices of crime_descriptions for given crime_cat
                                                                                 pivoted_slice[pivoted_slice.Policeuk_Cat.str.lower().isin([x.lower()])].Offence_Description.tolist(),
                                                                                 # make one choice
                                                                                 1,
                                                                                 # specify weights for selecting Crime_description
                                                                                 # if there isn't a match between two dataframes (for anti-social behaviour)
                                                                                 # just use Crime_type as Crime Description
                                                                                 # outcome: all Anti-social behaviour cases have that as crime description
                                                                                 p = pivoted_slice[pivoted_slice.Policeuk_Cat.str.lower().isin([x.lower()])].Number_of_Offences.tolist())[0] if len(pivoted_slice[pivoted_slice.Policeuk_Cat.str.lower().isin([x.lower()])]) > 0 else x)

        shortened_frame.Crime_description = shortened_frame.Crime_description.str.lower()

        list_of_slices.append(shortened_frame)

    populated_frame = pd.concat(list_of_slices)


    return populated_frame
