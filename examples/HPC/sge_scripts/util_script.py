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
from crime_sim_toolkit import utils

def main():

    load_pop(2017).to_csv('WY_pop_2017.csv', index=False)

    load_pop(2018).to_csv('WY_pop_2018.csv', index=False)

    # we'll use this crime dataframe to add demographic data
    big_crime_data = load_and_squash('wyp_data_2017/')


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

    big_crime_data = utils.populate_offence(big_crime_data)

    big_crime_data.to_csv('wyp_crime_2017.csv', index=False)

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

    file_list = glob.glob('WY_spenser_dat_small/*')

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
