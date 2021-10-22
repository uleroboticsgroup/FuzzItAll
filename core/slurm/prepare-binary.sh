#!/bin/bash
######################################################################
#
#   prepare-binary.sh - Bash script to build some source code in order
#                     to add fuzzer instrumentation to its output binary.
#
#   Usage: bash prepare-binary.sh <workingDir>
#
######################################################################

# load context variables
source FIA.config


# MAIN SCRIPT
# -------------------------------------------------------------------

if [[ "$#" -ne 1 ]];
then
    printf "*** Error! Incorrect number of arguments ***\n" >&2
    exit 22
fi

workingDir=$1

# move to target directory and load its configuration file
cd ${workingDir}
source ${FIA_TARGET_CONFIG_FILE}

# build target project with the wrapper compiler
printf "Building sources and adding instrumentation...\n"
env CC=${FIA_CC} CXX=${FIA_CXX} ${compilation_file} ${FIA_BUILD_FLAGS}
result=$?

exit ${result}