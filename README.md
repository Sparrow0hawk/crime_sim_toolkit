[![Build Status](https://travis-ci.com/Sparrow0hawk/crime_sim_toolkit.svg?branch=refactor_poisson)](https://travis-ci.com/Sparrow0hawk/crime_sim_toolkit)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5f1ccffc3bf64553b039e31afb638045)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Sparrow0hawk/crime_sim_toolkit&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/5f1ccffc3bf64553b039e31afb638045)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=Sparrow0hawk/crime_sim_toolkit&utm_campaign=Badge_Coverage)
# Crime data simulating toolkit

This package was built over the course of an internship at Leeds Institute of Data Analytics to simulate realistic crime data (predominantly for West Yorkshire) to generate as an input into an agent-based model.

The toolkit exists in three main strategies for data simualtion:
*   a simple poisson sampler based on past data
*   a decision tree using a wide range of predictor variables
*   a microsimulation using transition probabilities

The data_manipulation folder contains notebooks highlighting how some data sources have been constructed.

## Notes on datafiles

the census_2011_population_hh.csv file is derived from [ONS data](https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/2011censuspopulationandhouseholdestimatesforwardsandoutputareasinenglandandwales/rft-table-php01-2011-msoas-and-lsoas.zip). Taking data from sheet LSOA and using row 12 as the header row and keeping only rows below with data.

## To use

For the poisson simulator the package expects a raw dump of folders from [Police data](https://data.police.uk/) into data/policedata. If it can't find data there it will default to test data.

## TODO

*   Build method for using Police data API
*   microsimulation
