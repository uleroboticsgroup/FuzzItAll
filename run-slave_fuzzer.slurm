#!/bin/bash -x

#SBATCH --array=0
#SBATCH --ntasks=1
#SBATCH --mail-user=infbgd01@estudiantes.unileon.es
#SBATCH --mail-type=ALL 
#SBATCH --output=./log/SF-crashtest.%A_%a.out 
#SBATCH --error=./log/SF-crashtest.%A_%a.err 
#SBATCH --partition=haswell 
#SBATCH --qos=normal 
#SBATCH --time=3-23:55:00

#SBATCH --nodes=1
#SBATCH --tasks-per-node=1

# Add job to list
echo $SLURM_JOB_ID >> jobs.lst

# EPOCH (millisecons)
echo "## ## Starting step ${_step} at $(date) epoch $(date +%s%3N) ## ##"

srun bash -x slave-init.sh $1 $SLURM_JOB_ID

echo "## ## Completed step ${_step} at $(date) epoch $(date +%s%3N) ## ##"
