"""
File for defining some visualisation/mapping functions
"""
import requests
import pandas as pd
import folium
import branca
import pkg_resources

# Could be any dot-separated package/module name or a "Requirement"
resource_package = 'crime_sim_toolkit'


def get_choropleth(data=None, inline=True, counts_col='Counts'):
    """
    Function to produce a choropleth map based on passed counts data

    Inputs:
        data : a pandas dataframe with LSOA codes and a columns with count data
        inline : produce the map inline (in a ipynb) or output as html
        counts_col : name of the column with count data

    Outputs:
        m = a folium.Map object
    """

    # set colour map
    if (data[counts_col].unique().max() - data[counts_col].unique().min()) <= 20:

        # if data values range is small then just use max and min
        colorscale = branca.colormap.linear.YlOrRd_09.scale(data[counts_col].unique().min(),
                                                        data[counts_col].unique().max())

        colorscale = colorscale.to_step(n=5)

        colorscale.caption = 'Crime counts'

    # else if the data range is wider adopt a broader scale range
    else:
        colorscale = branca.colormap.linear.YlOrRd_09.scale(data[counts_col].describe()['25%'],
                                                        data[counts_col].describe()['75%'])

        colorscale = colorscale.to_step(n=5)

        colorscale.caption = 'Crime counts'

    # get crime counts per LSOA for given week in 2018
    choro_counts = data.groupby('LSOA_code')[counts_col].sum().reset_index('LSOA_code')

    LA_lst = []
    # get LA codes from LSOAs files
    for LSOA_cd in choro_counts.LSOA_code:

        LA_lst.append(match_LSOA_to_LA(LSOA_cd))

    # get unique LA codes
    LA_ser = pd.Series(LA_lst).unique()

    # get geojson data from unique LAs
    geodata = get_GeoJson(LA_ser.tolist())

    # build basic folium map
    m = folium.Map(location=[54.132393, -3.325583],
                   tiles='OpenStreetMap',
                   zoom_start=6)

    # adding popups to the map requires data to either be in geopandas format or within the geojson
    # geopandas throws a wobbly in colabs so we'll use a simple approach to adding the count data
    # into the geojson properties

    # narrow dataframe into just LSOA code and crime counts
    choro_counts = choro_counts.set_index('LSOA_code')[counts_col]

    #Loop over GeoJSON features and add the new properties
    for feat in geodata['features']:
        # set new property Count as the integer value of counts in a specific LSOA
        # using get to match the pandas series index (LSOA_code) to geojson lsoa code property
        # default zero here will handle missing LSOAs and return 0 counts
        feat['properties'][counts_col]=int(choro_counts.get(feat['properties']['LSOA11CD'], default=0))

    # define a style function that will colour lsoas based on crime counts
    # does not colour 0 black for unknown reason
    def style_func(feature):
        counted = choro_counts.get(feature['properties']['LSOA11CD'], default=0)
        return {
        'fillOpacity': 0.8,
        'weight' : 0.1,
        'fillColor': colorscale(counted)
        }


    # plot geojson file with style function including a tooltip
    folium.GeoJson(
          data=geodata,
          style_function=style_func,
          tooltip=folium.features.GeoJsonTooltip(['LSOA11CD',counts_col],
                                                aliases=['LSOA code',counts_col])
                                            ).add_to(m)

    # building a custom legend
    colorscale.add_to(m)
    # call display to show map

    if inline == True:
        display(m)
    else:
        # user can define map output name
        file_name = input('Please pass a name for your choropleth: ')

        m.save(pkg_resources.resource_filename(resource_package, 'output/')+str(file_name)+'.html')

    return m

def match_LSOA_to_LA(LSOA_cd):

    # load LSOA population frame
    # this contains LSOA code, MSOA code and LA names
    LSOA_pop = pd.read_csv(pkg_resources.resource_filename(resource_package, 'src/LSOA_data/census_2011_population_hh.csv'))

    row_of_interest = LSOA_pop.set_index('LSOA Code').loc[LSOA_cd]

    return row_of_interest['Local authority code']

def get_LA_GeoJson(LA_cd):
    """
    returns a link to LSOA geojson file within LA passed from https://github.com/martinjc/UK-GeoJSON/
    """

    link_base = 'https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/statistical/eng/lsoa_by_lad/'

    new_link = link_base+str(LA_cd)+'.json'

    return new_link


def get_GeoJson(LA_name):

    # get links to geojson files
    links = []

    for LA in LA_name:
        links.append(get_LA_GeoJson(LA))

    print('Total number of LAs passed.')
    # section for loading jsons into list

    geojson_lst = []

    for link in links:

        # use requests to load json file as dict
        # TODO: need to include some error catching for invalid requests
        geojson_lst.append(requests.get(link).json())

    for idx, json in enumerate(geojson_lst):

        counter1 = 0

        for feat in json['features']:

            counter1 += 1

        print('For file %s there are %s LSOAs' % (str(idx), str(counter1)))

    # combine geojsons
    start_json = dict(geojson_lst[0])

    # begin appending file by file ignoring first file
    for file in geojson_lst[1:]:

        for polygon in file['features']:

            start_json['features'].append(polygon)

    return start_json
