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

    # load all SPENSER populations for west yorkshire
    # populations in SPENSER are outputted at local authority level
    # the load_pop function opens all files and combines them into one
    # dataframe which here it writes out to disk
    load_pop(2017).to_csv('WY_pop_2017.csv', index=False)

    load_pop(2018).to_csv('WY_pop_2018.csv', index=False)

    # use the load_and_squash function to load all police data for 2017
    # (police data exists as series of sub directories for each month)
    # and combine it into one dataframe
    big_crime_data = load_and_squash('wyp_data_2017/')

    # load the population for 2017 to use for applying demographic proportions
    # to crime data
    pop_2017 = load_pop(2017)

    # on the population dataframe create a column of demographic class
    # with the format "SEX-AGE-ETHNICITY" by combining the separate
    # demographic category columns
    pop_2017['multi_cat_col'] = pop_2017.DC1117EW_C_SEX.astype(str) \
                                + '-' + pop_2017.DC1117EW_C_AGE.astype(str) \
                                + '-' + pop_2017.DC2101EW_C_ETHPUK11.astype(str)

    # create a pandas series of the proportion of each demographic class within the population
    demographic_prop = pop_2017['multi_cat_col'].value_counts() / pop_2017['multi_cat_col'].value_counts().sum()

    # we need to add demographic data to the crime data
    # to do that we take the proportions calculated above and randomly select a demographic class
    # by weighting choices based on the demographic proportions
    # these selected demographic proportions are added as a new column
    big_crime_data['victim_profile'] = big_crime_data\
    .apply(lambda x: np.random.choice(demographic_prop.index, p=demographic_prop.values), axis=1)

    # because we don't actually expect real data to have this combined demographic class column
    # so now we  split the victim_profile column into three separate columns
    expanded_demo = big_crime_data['victim_profile'].str.split('-', expand=True)

    expanded_demo.columns = ['sex','age','ethnicity']

    # and stick these columns back on the dataframe
    big_crime_data = pd.concat([big_crime_data, expanded_demo], axis=1)

    # we will also now drop lines with NaN in LSOA_code columns
    # we do this because of issues with the populate_offence function below
    # it drops 3-4% of offences in 2017 and 2018 respectively
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

if __name__ == '__main__':
    main()
