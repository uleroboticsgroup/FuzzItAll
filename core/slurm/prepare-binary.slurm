#!/bin/bash
######################################################################
#
#   prepare-binary.slurm - Slurm script for building some source code
#                        in order to add fuzzer instrumentation to its
#                        output binary.
#
#   Usage: sbatch --job-name="name" prepare-binary.slurm <workingDir>
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
#SBATCH --time=4-00:00:00


######################################################################
#### notifications
######################################################################
#SBATCH --mail-user=user@domain
#SBATCH --mail-type=END
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
srun bash slurm/prepare-binary.sh $1
result=$?
echo "#### Completed job '${SLURM_JOB_NAME}' at $(date) epoch $(date +%s%3N) ####"

exit ${result}