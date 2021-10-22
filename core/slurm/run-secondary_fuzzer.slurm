#!/bin/bash
######################################################################
#
#   run-secondary_fuzzer.slurm - Slurm script to run the secondary jobs
#                              that performs the fuzzing of a binary.
#
#   Usage: sbatch --job-name="name" [--dependency=after:prim_job_id] \
#                 run-secondary_fuzzer.slurm <workingDir> <number>
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
#### required packages
######################################################################
module purge
module load cascadelake/llvm_11.1.0_gcc9.2.0
module load cascadelake/gcc_9.2.0


######################################################################
#### run script
######################################################################
# add job to list of active fuzzers
echo ${SLURM_JOB_ID} >> jobs.lst

echo "#### Starting job '${SLURM_JOB_NAME}' at $(date) epoch $(date +%s%3N) ####"
srun bash ./slurm/run-secondary_fuzzer.sh $1 ${SLURM_JOB_ID}
result=$?
echo "#### Completed job '${SLURM_JOB_NAME}' at $(date) epoch $(date +%s%3N) ####"

exit ${result}