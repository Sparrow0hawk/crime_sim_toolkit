[![Build Status](https://travis-ci.com/Sparrow0hawk/crime_sim_toolkit.svg?branch=refactor_poisson)](https://travis-ci.com/Sparrow0hawk/crime_sim_toolkit)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5f1ccffc3bf64553b039e31afb638045)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Sparrow0hawk/crime_sim_toolkit&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/5f1ccffc3bf64553b039e31afb638045)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=Sparrow0hawk/crime_sim_toolkit&utm_campaign=Badge_Coverage)
[![PyPI version](https://badge.fury.io/py/crime-sim-toolkit.svg)](https://badge.fury.io/py/crime-sim-toolkit)
# Crime data simulating toolkit

This package was built over the course of an internship at Leeds Institute of Data Analytics to simulate realistic crime data (predominantly for West Yorkshire) to generate as an input into an agent-based model.

The toolkit exists in three main strategies for data simualtion:
*   a simple poisson sampler based on past data
*   a decision tree using a wide range of predictor variables
*   a microsimulation using transition probabilities

The data_manipulation folder contains notebooks highlighting how some data sources have been constructed.

## Installation

This package is now available via PyPi.

```{bash}
pip install crime_sim_toolkit
```

For examples of useage checkout this example [notebook](https://github.com/Sparrow0hawk/crime_sim_toolkit/blob/master/examples/crime_sim_poisson_example.ipynb).
## Notes on datafiles

the census_2011_population_hh.csv file is derived from [ONS data](https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/2011censuspopulationandhouseholdestimatesforwardsandoutputareasinenglandandwales/rft-table-php01-2011-msoas-and-lsoas.zip). Taking data from sheet LSOA and using row 12 as the header row and keeping only rows below with data.

## To use

The expected input data for this package is from [Police data UK](https://data.police.uk/). If it can't find data there it will default to test data.

```{python}
import crime_sim_toolkit.poisson_sim as Poisson_sim


sim_week = Poisson_sim.Poisson_sim(
                               # specify the local authorities to look at (all five for West Yorkshire here)
                               LA_names=['Kirklees','Calderdale','Leeds','Bradford','Wakefield'],
                               # specify the path to the top level directory containing PoliceUK data
                               directory='/root/crime_sim_toolkit/sample_data',
                               # this can either be Day or Week
                               timeframe='Day',
                               # do you want to aggregate data to Police Force
                               aggregate=True)

# view the head of the generated pandas dataframe
sim_week.data.head()

datetime 	Crime_type 	LSOA_code 	Counts
0 	2017-01-01 	Anti-social behaviour 	West Yorkshire 	147
1 	2017-01-01 	Bicycle theft 	West Yorkshire 	7
2 	2017-01-01 	Burglary 	West Yorkshire 	65
```

This will create an object that contains the PoliceUK data formated into counts by crime type, by LSOA (or Police force) by timeframe. Forecasts can be generated using this transformed past data as shown in the [example notebooks](https://github.com/Sparrow0hawk/crime_sim_toolkit/tree/master/examples).

## TODO

*   Build method for using Police data API
*   microsimulation
