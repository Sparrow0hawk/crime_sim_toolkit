"""
a simple python script for running the microsimulation from
the crime_sim_toolkit

This file expects datafiles to already have been produced.
Datafiles expected to exist in one directory (update data_dir variable to specify)
"""
import os
import crime_sim_toolkit.microsim as Microsim

def main():

    simulation_0 = Microsim.Microsimulator()

    # specifing the directory path to where the test data is for this example
    data_dir = '.'

    simulation_0.load_data(
                           # we specify the seed year, this is the year from which crime probabilities are determined
                           seed_year = 2017,
                           # a string to the directory where your police data is (police data explained above)
                           police_data_dir = os.path.join(data_dir,'wyp_crime_2017.csv'),
                           # a string to the directory where the population for the seed year is
                           # this is a synthetic population generated using SPENSER
                           seed_pop_dir = os.path.join(data_dir,'WY_pop_2017.csv'),
                           # the demographic columns for the seed synthetic population
                           spenser_demographic_cols = ['DC1117EW_C_SEX','DC1117EW_C_AGE','DC2101EW_C_ETHPUK11'],
                           # the columns that correspond to the demographic data in the police data
                           police_demographic_cols = ['sex','age','ethnicity']
                           )

    simulation_0.load_future_pop(
                                 # the directory to where synthetic populations are
                                 synthetic_population_dir=os.path.join(data_dir),
                                 # which years population the user wishes to load
                                 year=2018,
                                 # the demographic columns within the dataset
                                 demographic_cols=['DC1117EW_C_SEX','DC1117EW_C_AGE','DC2101EW_C_ETHPUK11']
                                 )

    simulation_0.generate_probability_table()

    sim_output = simulation_0.run_mp_simulation()

    print('The shape of simulated data is: ',sim_output.shape)

    print('The proportion of crimes to population in seed data is:', simulation_0.crime_data.shape[0] / simulation_0.seed_population.shape[0])

    print('The proportion of simulated crimes within the population is: ', sim_output.shape[0] / simulation_0.future_population.shape[0])

    sim_output.to_csv('simulation_output_'+str(os.environ['JOB_ID'])+'.csv')

if __name__ = '__main__':

    main()
