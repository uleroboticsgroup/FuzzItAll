#!/bin/bash -x

#SBATCH --array=0
#SBATCH --ntasks=1
#SBATCH --mem=1gb                   # Job Memory
#SBATCH --mail-user=infbgd01@estudiantes.unileon.es
#SBATCH --mail-type=END  # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --output=./log/MF-crashtest.%A_%a.out 
#SBATCH --error=./log/MF-crashtest.%A_%a.err 
#SBATCH --partition=haswell 
#SBATCH --qos=normal 
#SBATCH --time=4-0:00:00

#SBATCH --nodes=1              # Number of nodes
#SBATCH --ntasks=1             # Number of MPI ranks

# Add job to list
echo $SLURM_JOB_ID >> jobs.lst

# EPOCH (millisecons) $(date +%s%3N)
echo "## ## Starting step ${_step} at $(date) epoch $(date +%s%3N) ## ##"

srun bash -x master-init.sh $1

echo "## ## Completed step ${_step} at $(date) epoch $(date +%s%3N) ## ##"
