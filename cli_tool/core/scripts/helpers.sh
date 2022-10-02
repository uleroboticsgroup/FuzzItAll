#!/bin/bash
######################################################################
#
# helpers.sh - Helper library for the FuzzItAll command line tool.
#
######################################################################

# force script termination if a pipeline returns a non-zero status
set -e

# import current FuzzItAll configuration
source "${FIA_ROOT}FIA.config"


# FUNCTIONS
#---------------------------------------------------------------------

######################################################################
# Print version of the tool.
# Globals (from FIA.config):
#   FIA_ROOT
#   FIA_VERSION
# Arguments:
#   None
# Output:
#   Writes to stdout the tool version.
######################################################################
function fuzzitall::version() {
  source "${FIA_ROOT}version"

  printf "\nFuzzItAll command line tool (v%s)\n\n" "${FIA_VERSION}"
}

######################################################################
# Print an error.
# Arguments:
#   Message describing the cause of the error.
# Outputs:
#   Writes an error message to stderr.
######################################################################
function fuzzitall::error() {
  printf "[$(date +'%Y-%m-%d %T')]: $*\n" 1>&2
}

######################################################################
# Log a message.
# Globals (from FIA.config):
#   FIA_ROOT
# Arguments:
#   Message to be logged.
# Outputs:
#   Writes a message to the log file.
######################################################################
function fuzzitall::log() {
  printf "[$(date +'%Y-%m-%d %T')]: $*\n" >> "${FIA_ROOT}log/log.txt"
}

######################################################################
# Display a message and then terminate the script execution.
# Arguments:
#   Message describing the cause of the stop.
# Outputs:
#   Writes the cause of stop to stderr.
# Returns:
#   Exit code 1 (operation not permitted).
######################################################################
function fuzzitall::die() {
  local last_exit_status=$?

  fuzzitall::error "FATAL ERROR - $* (status ${last_exit_status})\n"

  exit 1
}

######################################################################
# Get the path to the control script of a given fuzzer.
# Globals (from FIA.config):
#   FIA_FUZZERS_DIRECTORY
# Arguments:
#   Name of the fuzzer.
# Returns:
#   Path to the control script of the fuzzer.
######################################################################
function fuzzitall::get_fuzzer() {
  local fuzzer_name=$1

  # return the path to the given fuzzer
  echo "${FIA_FUZZERS_DIRECTORY}${fuzzer_name}/fuzzer"
}

######################################################################
# Extract the identifier of the Slurm job attributed to the submission
# of a script using the sbatch command. After submitting a script, the
# output looks like this: "Submitted batch job <job_identifier>".
# Arguments:
#   Output obtained after submitting a Slurm script with the sbatch command.
# Returns:
#   Slurm job identifier.
######################################################################
function fuzzitall::get_slurm_job_id() {
  local job_output=$1

  # extract the identifier
  local job_id
  job_id="$(echo ${job_output} | rev | cut -f 1 -d ' ' | rev)"

  # and return it
  echo "${job_id}"
}
