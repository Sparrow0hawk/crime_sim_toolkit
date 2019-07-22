"""
File for defining some visualisation/mapping functions
"""
import pandas as pd
import glob
import folium
import branca
import json
import requests
import time
from IPython.display import display, clear_output

def get_choropleth(data=None, inline=True):

    # set colour map
    colorscale = branca.colormap.linear.YlOrRd_09.scale(data.describe()['25%'],
                                                        data.describe()['75%'])


    # get web geojson LSOA polygons for West Yorkshire from my github
    geojson_data = json.load('https://raw.githubusercontent.com/Sparrow0hawk/policedata_dump/master/WY_geojson.geojson')

    # read request as a json
    WY_geodata = geojson_data.json()

    # build basic folium map instance centered on leeds
    m = folium.Map(location=[53.816497, -1.536751],
                             tiles='OpenStreetMap',
                             zoom_start=10)

    # get crime counts per LSOA for given week in 2018
    choro_counts = simulated_year_frame[simulated_year_frame.Week == week].groupby(['Week','LSOA_code'])['Count'].sum().reset_index(['Week','LSOA_code'])

    # narrow dataframe into just LSOA code and crime counts
    choro_counts = choro_counts.set_index('LSOA_code')['Count']

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
                                                aliases=['LSOA code','Crime count (simulated)'])
                                            ).add_to(m)

    # call display to show map

    if inline == True:
        display(m)
    else:
        m.save('/output/choropleth.html')

def match_LSOA_to_LA(LSOA_cd):

    # load LSOA population frame
    # this contains LSOA code, MSOA code and LA names
    LSOA_pop = pd.read_csv('./src/LSOA_data/census_2011_population_hh.csv')

    row_of_interest = LSOA_pop.set_index('LSOA Code').loc[LSOA_cd]

    return row_of_interest['Local authority code']
