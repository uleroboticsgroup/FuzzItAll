#!/bin/bash
######################################################################
#
# run-fuzzing.slurm - Submission script to run fuzzing tasks on a project.
#
######################################################################


### BEGIN_JOB_DESCRIPTION ###
# DO NOT EDIT THIS BLOCK, IT WILL BE GENERATED DURING DEPLOYMENT.
### END_JOB_DESCRIPTION ###


######################################################################
### run program
######################################################################
if [[ -z ${SLURM_ARRAY_TASK_ID} ]]; then
  echo "### Starting job '${SLURM_JOB_NAME}' at $(date) ###"
fi

task_number="${SLURM_ARRAY_TASK_ID}/${SLURM_ARRAY_TASK_COUNT}"

echo "###### Starting task '${task_number}' at $(date) ######"

project_directory=$1
fuzzer_name=$2

srun bash ./run-fuzzing \
  -p "${project_directory}" -f "${fuzzer_name}" -t "${SLURM_ARRAY_TASK_ID}"
result=$?

echo "###### Completed task '${task_number}' at $(date) ######"

if [[ -z ${SLURM_ARRAY_TASK_ID} ]]; then
  echo "### Completed job '${SLURM_JOB_NAME}' at $(date) ###"
fi

exit ${result}
