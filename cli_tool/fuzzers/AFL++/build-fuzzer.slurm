#!/bin/bash
######################################################################
#
# build-fuzzer.slurm - Submission script to build AFL++.
#
######################################################################


### BEGIN_JOB_DESCRIPTION ###
# DO NOT EDIT THIS BLOCK, IT WILL BE GENERATED DURING DEPLOYMENT.
### END_JOB_DESCRIPTION ###


######################################################################
### run program
######################################################################
echo "### Starting job '${SLURM_JOB_NAME}' at $(date) ###"

target_directory=$1

srun bash ./build-fuzzer -d "${target_directory}"
result=$?

echo "### Completed job '${SLURM_JOB_NAME}' at $(date) ###"

exit ${result}
