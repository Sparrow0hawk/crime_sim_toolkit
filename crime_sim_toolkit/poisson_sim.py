# TODO big tidy up and refactor into something neater and callable
# lets expand our random crime count sampler

# lets build in randon sampling at an LSOA level
# lets split available month-to-month data into weeks of the year as day by day sampling was poor
# lets also build back into the policedata LSOAs with no crime
# USES POISSON

# import libraries

import pandas as pd
import numpy as np
import glob
from calendar import monthrange
import matplotlib.pyplot as plt
import scipy.stats
import math


def initialise_data(LA_names=['Bradford','Calderdale', 'Kirklees', 'Leeds', 'Wakefield']):
    """
    Function to initialise dataset

    This will load data from the embedded data folder (src) and user passed dataset

    Input: LA_names : local authority names, python list of capitalised strings of local authority names
           src folder
           data folder: populated with monthly csv files from custom downloads from https://data.police.uk/data/
    """

    # boot up LSOA lists from 2011 census, this has been filtered for just west yorkshire

    LSOA_pop = pd.read_csv('./src/census_2011_population_hh.csv')

    LSOA_pop = LSOA_pop[LSOA_pop['Local authority name'].isin(LA_names)]

    LSOA_counts_WY = LSOA_pop[['LSOA Code','LSOA Name','Persons','Households']].reset_index(drop=True)

    LSOA_counts_WY.columns = ['LSOA_code','LSOA_name','persons','households']

    LSOA_counts_WY.persons = LSOA_counts_WY.persons.apply(lambda x: np.int64(x.replace(',', '')))

    LSOA_counts_WY.households = LSOA_counts_WY.households.apply(lambda x: np.int64(x.replace(',', '')))

    LSOA_counts_WY.head()

files_dir = glob.glob('/content/policedata*/*/2*')

files_combo = []

for x in files_dir:

    open_file = pd.read_csv(x)
    files_combo.append(open_file)

combined_files = pd.concat(files_combo, axis=0)

combined_files.reset_index(inplace=True, drop=True)

combined_files.head()

combined_files['Year'] = combined_files['Month'].map(lambda x: pd.to_datetime(x).year)

combined_files['Mon'] = combined_files['Month'].map(lambda x: pd.to_datetime(x).month)

combined_files['Day'] = combined_files['Month'].map(lambda x: np.random.randint(1,monthrange(pd.to_datetime(x).year, pd.to_datetime(x).month)[1] +1))

combined_files['Week'] = combined_files.apply(lambda x: pd.to_datetime([str(x.Year)+'/'+str(x.Mon)+'/'+str(x.Day)]).week[0], axis=1)

combined_files.head()

combined_files['Week'].value_counts().sort_index().plot.bar()

combined_files['Day'].value_counts().sort_index().plot.bar()

combined_files.sort_values(by='Month').groupby(['Year','Mon'])['Week'].value_counts()

# right both data sets are ready for the generation of transition probabilities of crime in each LSOA

tot_counts = pd.DataFrame(combined_files.groupby(['Year','Mon','Crime type','LSOA code'])['Week'].value_counts()).reset_index(level=['Mon','Crime type','Year','LSOA code'])

print(tot_counts.columns)

tot_counts.columns = ['Year', 'Mon', 'Crime_type','LSOA_code', 'Counts']

tot_counts.reset_index(inplace=True)

# filter for just WY LSOA

tot_counts = tot_counts[tot_counts.LSOA_code.isin(LSOA_counts_WY.LSOA_code)]

tot_counts.reset_index(inplace=True, drop=True)

tot_counts.head()

tot_counts.LSOA_code.isin(LSOA_counts_WY.LSOA_code).shape

LSOA_counts_WY.LSOA_code.unique().shape

frame1 = tot_counts[tot_counts.Year == 2016]

frame1 = frame1[frame1.Week == 33]

frame1.head()

LSOA_counts_WY.LSOA_code[~LSOA_counts_WY.LSOA_code.isin(frame1.LSOA_code)].tolist()

pile_o_df = []

for year in tot_counts.Year.unique():

    year_frame = tot_counts.copy()

    year_frame = year_frame[year_frame.Year == year]

    for wk in year_frame.Week.unique():

        wk_frame = year_frame[year_frame.Week == wk]

        for crim_typ in tot_counts['Crime_type'].unique():

            sliced_frame = wk_frame[wk_frame.Crime_type == crim_typ]

            missing_LSOA = LSOA_counts_WY.LSOA_code[~LSOA_counts_WY.LSOA_code.isin(sliced_frame.LSOA_code)].tolist()

            new_fram = pd.DataFrame(missing_LSOA, columns=['LSOA_code'], index=range(len(missing_LSOA)))

            new_fram['Crime_type'] = crim_typ

            new_fram['Counts'] = 0

            new_fram['Mon'] = sliced_frame.Mon.unique().tolist()[0]

            new_fram['Week'] = sliced_frame.Week.unique().tolist()[0]

            new_fram['Year'] = sliced_frame.Year.unique().tolist()[0]

            pile_o_df.append(new_fram)


new_tot_counts = pd.concat([tot_counts,pd.concat(pile_o_df)], sort=True)

new_tot_counts.reset_index(drop=True, inplace=True)

new_tot_counts.head()

new_tot_counts.info()

# check whether each week has the same number of unique LSOAs (indicating zero results have been filled in)

for year in new_tot_counts.Year.unique():

    print(year)

    year_frame = new_tot_counts.copy()

    year_frame = year_frame[year_frame.Year == year]

    for wk in year_frame.Week.unique():

        wk_frame = year_frame[year_frame.Week == wk]

        print('For week: '+str(wk)+' number of unique LSOAs: '+str(len(wk_frame.LSOA_code.unique())))

new_tot_counts.Counts.value_counts().plot.bar()

# with this amended dataset lets try and do forecasting. This due to dimensions may take a long time/fail on this machine

new_tot_counts[(new_tot_counts.Year == 2017) & (new_tot_counts.Mon == 12)].Week.unique()

new_tot_counts.shape

# create a frame for out-of-bag sampling to compare against 2018 crime count

oob_crime_counts = new_tot_counts[(new_tot_counts.Year != 2018) & (new_tot_counts.Year != 2019)]

oob_crime_counts.shape

"""%%time

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
"""

simulated_year_frame.head()

simulated_year_frame.shape

# this takes a very long time, quite a lot of dimensions going on.

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

# starting to think about mapping it

import folium
import branca
import json
import requests
import time
from IPython.display import display, clear_output

# set colour map
colorscale = branca.colormap.linear.YlOrRd_09.scale(1, 25)

# iteratively get folium map for each week
for week in new_tot_counts.Week.sort_values().unique():

  # get web geojson LSOA polygons for West Yorkshire from my github
  geojson_data = requests.get('https://raw.githubusercontent.com/Sparrow0hawk/policedata_dump/master/WY_geojson.geojson')

  # read request as a json
  WY_geodata = geojson_data.json()

  # build basic folium map instance centered on leeds
  m = folium.Map(location=[53.752288, -1.677899],
            tiles='OpenStreetMap',
            zoom_start=10)

  # get crime counts per LSOA for given week in 2018
  choro_counts = new_tot_counts[(new_tot_counts.Week == week) & (new_tot_counts.Year == 2018)].groupby(['Week','LSOA_code'])['Counts'].sum().reset_index(['Week','LSOA_code'])

  # narrow dataframe into just LSOA code and crime counts
  choro_counts = choro_counts.set_index('LSOA_code')['Counts']

  # adding popups to the map requires data to either be in geopandas format or within the geojson
  # geopandas throws a wobbly in colabs so we'll use a simple approach to adding the count data
  # into the geojson properties

  #Loop over GeoJSON features and add the new properties
  for feat in WY_geodata['features']:
    # set new property Count as the integer value of counts in a specific LSOA
    # using get to match the pandas series index (LSOA_code) to geojson lsoa code property
    feat['properties']['Count']=int(choro_counts.get(feat['properties']['LSOA11CD']))

  # define a style function that will colour lsoas based on crime counts
  # does not colour 0 black for unknown reason
  def style_func(feature):
    counted = choro_counts.get(feature['properties']['LSOA11CD'])
    return {
        'fillOpacity': 0.7,
        'weight': 0.3,
        'fillColor': '#black' if counted == 0 else colorscale(counted)
    }


  # plot geojson file with style function including a tooltip
  folium.GeoJson(
      data=WY_geodata,
      style_function=style_func,
      tooltip=folium.features.GeoJsonTooltip(['LSOA11CD','Count'],
                                            aliases=['LSOA code','Crime count (actual)']),

      highlight_function=lambda x: {'weight':3,
                                      'color':'black',
                                      'fillOpacity':0.8}
  ).add_to(m)

  # call display to show map
  display(m)

  # sleep for 8s for inspection
  time.sleep(8)

  # clear output to generate new map
  clear_output()



# lets calculate the difference between the prediction and the actual

comparison_frame = pd.concat([simulated_year_frame.groupby(['Week','LSOA_code'])['Count'].sum(), new_tot_counts[new_tot_counts.Year == 2018].groupby(['Week','LSOA_code'])['Counts'].sum()],axis=1)

comparison_frame.reset_index('Week', inplace=True)

comparison_frame.columns = ['Week','Pred_counts','Actual']

comparison_frame.head()

comparison_frame['Difference'] = abs(comparison_frame.Pred_counts - comparison_frame.Actual)

from sklearn.metrics import mean_squared_error, median_absolute_error, mean_absolute_error

y_rmse = np.sqrt(mean_squared_error(comparison_frame.Actual, comparison_frame.Pred_counts))

y_ame = mean_absolute_error(comparison_frame.Actual, comparison_frame.Pred_counts)

y_medae = median_absolute_error(comparison_frame.Actual, comparison_frame.Pred_counts)

print('Root mean squared error of poisson sampler: ',round(y_rmse, 1))

print('Mean absolute error: ', round(y_ame, 1))

print('Median absolute error: ', round(y_medae, 1))

comparison_frame['Difference'].sum() / len(comparison_frame)

comparison_frame[['Pred_counts','Actual']].plot.scatter(x='Actual',y='Pred_counts')
plt.plot([0,175],[0,175], 'k--')
