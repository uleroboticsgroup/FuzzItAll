#!/bin/bash
######################################################################
#
#   build-AFL++.slurm - Slurm script to build AFL++.
#
#   Usage: sbatch --job-name="name" build-AFL++.slurm <installDir>
#
######################################################################

######################################################################
#### job blueprint
######################################################################
#SBATCH --partition=cascadelake
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --tasks-per-node=1
#SBATCH --qos=normal
#SBATCH --time=0-00:10:00


######################################################################
#### notifications
######################################################################
#SBATCH --mail-user=user@domain
#SBATCH --mail-type=ALL
#SBATCH --output=./log/%x_%A_%a.out
#SBATCH --error=./log/%x_%A_%a.err


######################################################################
#### required modules
######################################################################
module purge
module load cascadelake/llvm_11.1.0_gcc9.2.0
module load cascadelake/gcc_9.2.0


######################################################################
#### run program
######################################################################
echo "#### Starting job '${SLURM_JOB_NAME}' at $(date) epoch $(date +%s%3N) ####"
srun bash build-AFL++.sh $1
result=$?
echo "#### Completed job '${SLURM_JOB_NAME}' at $(date) epoch $(date +%s%3N) ####"

exit ${result}