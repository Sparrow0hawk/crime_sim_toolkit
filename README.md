# Crime data simulating toolkit

This package was built over the course of an internship at Leeds Institute of Data Analytics to simulate realistic crime data (predominantly for West Yorkshire) to generate as an input into an agent-based model.

The toolkit exists in three main strategies for data simualtion:
* a simple poisson sampler based on past data
* a decision tree using a wide range of predictor variables
* a microsimulation using transition probabilities


## Notes on datafiles

the census_2011_population_hh.csv file is derived from [ONS data] (https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/2011censuspopulationandhouseholdestimatesforwardsandoutputareasinenglandandwales/rft-table-php01-2011-msoas-and-lsoas.zip). Taking data from sheet LSOA and using row 12 as the header row and keeping only rows below with data.
