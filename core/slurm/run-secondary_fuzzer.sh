#!/bin/bash
######################################################################
#
#   run-secondary_fuzzer.sh - Bash script to run the secondary job that
#                           performs the task of fuzzing a binary. The
#                           script only starts if there is a master job
#                           already running.
#
#   Usage: ./run-secondary_fuzzer.sh <workingDir> <secondary_job_counter>
#
######################################################################

# load context variables
source FIA.config
source $1/${FIA_TARGET_CONFIG_FILE}


# SCRIPT VARS
# --------------------------------------------------------------------
readonly _PRIMARY_FUZZER_FILENAME="primary-fuzzer.name"
readonly _FUZZER_OUTPUT_DIRNAME="fuzz-out"


# MAIN SCRIPT
# -------------------------------------------------------------------

workingDir=$1
secondaryJobCounter=$2

primaryFuzzerFilePath="${workingDir}${_PRIMARY_FUZZER_FILENAME}"
outputDir="${workingDir}${_FUZZER_OUTPUT_DIRNAME}"
fuzzerName="${secondaryJobCounter}"

# check if primary fuzzer is alive
if [[ -f ${primaryFuzzerFilePath} ]];
then
  env ${FIA_FUZZ_FLAGS} ${FIA_FUZZ} -i ${workingDir}${corpus_path} \
                                    -o ${outputDir} \
                                    -S ${fuzzerName} \
                                    ${workingDir}${run}
  result=$?
else
  projectName=`echo ${primaryFuzzerFilePath} | rev | cut -d/ -f1 | cut -d. -f2 | rev`
  printf "Error! There is no primary fuzzer running for '${projectName}'." >&2
  printf "The secondary job cannot start.\n" >&2
  exit 22
fi

exit ${result}