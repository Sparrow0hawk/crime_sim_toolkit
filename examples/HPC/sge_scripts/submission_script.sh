# an example submission script for using the crime_sim_toolkit Microsimulator
# Alex Coleman, a.coleman1@leeds.ac.uk, 2020-03-31

# use current environment and current working dir
#$ -cwd -V

# specify job time limit (min 15min, max 48h)
#$ -l h_rt=10:00:00

# specify the memory requirement for the job
#$ -l h_vmem=8G

# set notifications
#$ -m be
#$ -M a.coleman1@leeds.ac.uk

# main job
conda activate crime-sim

python microsim_batch.py
