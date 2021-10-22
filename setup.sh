#!/bin/bash
######################################################################
#
#   setup.sh - Bash script to deploy FuzzItAll.
#
#   Usage: ./setup.sh <installDir>
#
######################################################################

# FUNCTIONS
# --------------------------------------------------------------------

function print_usage
{
   printf "$0 - FuzzItAll setup script\n\n"
   printf "Usage: ./$0 [install|uninstall] <installDir>\n"
}

function install_fia_core
{
    local installDir=$1

    printf "*** Installing FuzzItAll core files into '${installDir}' ***\n"

    if [[ -d "${installDir}" ]];
    then
        printf "Error! Directory '${installDir}' exists. Aborting installation.\n" >&2
        exit 22
    fi

    # create directory
    mkdir -p ${installDir}

    # copy core files into it
    cp -r core/* ${installDir}

    # update FIA.config with the new path
    sed -i "s|FIA_ROOT=\"\"|FIA_ROOT=\"${installDir}/\"|g" "${installDir}/FIA.config"

    # create log folder
    mkdir -p "${installDir}/log"

    # give execution permissions to fuzzitall and utils scripts
    chmod +x "${installDir}/fuzzitall"
    chmod +x "${installDir}/utils/manage_jobs.sh"
    chmod +x "${installDir}/utils/status.sh"
}

function install_fuzzers
{
    local installDir=$1

    cd $(pwd)"/external/AFL++/"

    printf "*** Building AFL++ ***\n"
    local jobName="FuzzItAll-BuildAFL++"
    sbatch --job-name=${jobName} build-AFL++.slurm "${installDir}"

    printf "\tPlease check $(pwd)/log/ for more information\n"
}


# MAIN SCRIPT
# --------------------------------------------------------------------

# check usage
if [[ $# -eq 0 ]];
then
   printf "Error! No arguments supplied.\n" >&2
   print_usage
   exit 22
fi

installDir=$1

install_fia_core "${installDir}"
install_fuzzers "${installDir}"

exit 0