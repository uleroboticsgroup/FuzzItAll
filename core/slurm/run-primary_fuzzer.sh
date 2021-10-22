#!/bin/bash
######################################################################
#
#   run-primary_fuzzer.sh - Bash script to run the primary job that
#                         performs the task of fuzzing a binary. The
#                         script either starts a new fuzzing task or
#                         continues a previous one.
#
#   Usage: ./run-primary_fuzzer.sh <workingDir> <slurmJobID>
#
######################################################################

# load context variables
source FIA.config
source $1/${FIA_TARGET_CONFIG_FILE}


# SCRIPT VARS
# --------------------------------------------------------------------
readonly _PRIMARY_FUZZER_FILENAME="primary-fuzzer.name"
readonly _FUZZER_OUTPUT_DIRNAME="fuzz-out"


# FUNCTIONS
# --------------------------------------------------------------------

function check_primary_fuzzer_existence
{
  local primaryFuzzerFile=$1

  # check if previous fuzzing job is still running
  local fuzzerPrevJobID=$(cat ${primaryFuzzerFile})
  local fuzzerPrevJobState=$(squeue --noheader | grep ${fuzzerPrevJobID})

  # set return flag
  local prevFuzzerExists=1
  if [[ -z "${fuzzerPrevJobState}" ]];
  then
    prevFuzzerExists=0
  fi

  echo ${prevFuzzerExists}
}

function fuzz_binary
{
  workingDir=$1
  fuzzerName="$2"

  outputDir=${workingDir}${_FUZZER_OUTPUT_DIRNAME}

  # do we have to recover the previous fuzzing task or rather create a new one?
  if [[ -d "${outputDir}" ]];
  then
    # recover previous task
    env ${FIA_FUZZ_FLAGS} ${FIA_FUZZ} -i - -o ${outputDir} \
                                      -M ${fuzzerName} \
                                      ${workingDir}${run}
    result=$?
  else
    # create a new one
    env ${FIA_FUZZ_FLAGS} ${FIA_FUZZ} -i ${workingDir}${corpus_path} \
                                      -o ${outputDir} \
                                      -M ${fuzzerName} \
                                      ${workingDir}${run}
    result=$?
  fi

  echo ${result}
}


# MAIN SCRIPT
# --------------------------------------------------------------------

workingDir=$1
slurmJobID=$2

primaryFuzzerFilePath="${workingDir}${_PRIMARY_FUZZER_FILENAME}"

# check if primary fuzzer is alive
if [[ -f ${primaryFuzzerFilePath} ]];
then
  primaryFuzzerIsAlive=$(check_primary_fuzzer_existence "${primaryFuzzerFilePath}")

  if (( ${primaryFuzzerIsAlive} ));
  then
    projectName=`echo ${primaryFuzzerFilePath} | rev | cut -d/ -f1 | cut -d. -f2 | rev`
    printf "Error! A primary fuzzer for '${projectName}' already exists " >&2
    printf "with job ID '${prevFuzzJobID}'. Fuzzing will be cancelled.\n" >&2
    exit 22
  else
    # update slurm job ID
    slurmJobID=$(cat ${primaryFuzzerFilePath})
  fi
fi

# update primary fuzzer jobID
echo ${slurmJobID} > ${primaryFuzzerFilePath}

# fuzz binary from target project
fuzz_binary "${workingDir}" "${slurmJobID}"
result=$?

exit ${result}