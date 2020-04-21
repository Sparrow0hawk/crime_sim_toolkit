[![Build Status](https://travis-ci.com/Sparrow0hawk/crime_sim_toolkit.svg?branch=refactor_poisson)](https://travis-ci.com/Sparrow0hawk/crime_sim_toolkit)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5f1ccffc3bf64553b039e31afb638045)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Sparrow0hawk/crime_sim_toolkit&amp;utm_campaign=Badge_Grade)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Sparrow0hawk_crime_sim_toolkit&metric=alert_status)](https://sonarcloud.io/dashboard?id=Sparrow0hawk_crime_sim_toolkit)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/5f1ccffc3bf64553b039e31afb638045)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=Sparrow0hawk/crime_sim_toolkit&utm_campaign=Badge_Coverage)
[![PyPI version](https://badge.fury.io/py/crime-sim-toolkit.svg)](https://badge.fury.io/py/crime-sim-toolkit)
# Crime data simulating toolkit

The crime_sim_toolkit is a python package that originated from a joint [Alan Turing Institute](https://www.turing.ac.uk/research/research-projects/agent-based-models-police-resourcing-and-demand) and [Leeds Institute of Data Analytics](https://lida.leeds.ac.uk/research-projects/forecasting-the-future-of-policing/) project formulated by [Dr. Dan Birks](https://essl.leeds.ac.uk/law/staff/261/dr-daniel-birks) at the University of Leeds. It focuses on generating simulations of crime demand, using alternate methodologies, that can then be used as an input into an agent based model of police supply.

The toolkit was envisioned to have three main strategies for data simulation:
*   a simple poisson sampler based on past data
*   a decision tree using a wide range of predictor variables (TODO)
*   a microsimulation using transition probabilities

The data_manipulation folder contains notebooks highlighting how some data sources have been constructed.

## Installation

### Install via Python package index

This package is now available via [PyPi](https://pypi.org/project/crime-sim-toolkit/).

```{bash}
pip install --user crime_sim_toolkit
```

### Install from sources

You can also install this package from source by cloning this repository, navigating into the `crime_sim_toolkit`
directory and running the following.

```{bash}
python setup.py install --user
```

## Wiki

Find out how to get started using the `crime_sim_toolkit` via our [Wiki](https://github.com/Sparrow0hawk/crime_sim_toolkit/wiki)

## License

[MIT License](https://github.com/Sparrow0hawk/crime_sim_toolkit/blob/master/LICENSE)

## Notes on datafiles

The census_2011_population_hh.csv file is derived from [ONS data](https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/2011censuspopulationandhouseholdestimatesforwardsandoutputareasinenglandandwales/rft-table-php01-2011-msoas-and-lsoas.zip). Taking data from sheet LSOA and using row 12 as the header row and keeping only rows below with data.

## TODO

*   Build method for using Police data API
*   Decision tree implementation
