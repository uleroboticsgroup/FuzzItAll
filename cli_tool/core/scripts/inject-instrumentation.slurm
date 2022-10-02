#!/bin/bash
######################################################################
#
# inject-instrumentation.slurm - Submission script to inject instrumentation
#                                into the source code of a project.
#
######################################################################


### BEGIN_JOB_DESCRIPTION ###
# DO NOT EDIT THIS BLOCK, IT WILL BE GENERATED DURING DEPLOYMENT.
### END_JOB_DESCRIPTION ###


######################################################################
### run program
######################################################################
echo "### Starting job '${SLURM_JOB_NAME}' at $(date) ###"

project_directory=$1
fuzzer_name=$2

srun bash ./inject-instrumentation \
  -p "${project_directory}" -f "${fuzzer_name}"
result=$?

echo "### Completed job '${SLURM_JOB_NAME}' at $(date) ###"

exit ${result}
