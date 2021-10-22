#!/bin/bash
######################################################################
#
#   build-AFL++.sh - Bash script to build AFL++ (both regular and with
#                  sanitizers support). This script assumes that AFL++
#                  source code is in current working directory.
#
#   Usage: bash build-AFL++.sh <installDir>
#
######################################################################

# SCRIPT VARS
# --------------------------------------------------------------------

readonly _AFL_VERSION="3.14c"

readonly _BUILD_DIR=$(pwd)"/build"


# FUNCTIONS
# --------------------------------------------------------------------

function setup
{
    local installDir=$1

    printf "*** Creating directories ***\n"
    if [[ ! -d "${_BUILD_DIR}" ]];
    then
        mkdir -p ${_BUILD_DIR}
    fi
    if [[ ! -d "${installDir}" ]];
    then
        mkdir -p "${installDir}"
    fi

    printf "*** Unzipping AFL++ ${_AFL_VERSION} source ***\n"
    local aflSource="${_AFL_VERSION}.zip"
    if [[ ! -f "${aflSource}" ]];
    then
        printf "*** Error! AFL++ sources not found! ***\n" >&2
        exit 2
    fi
    unzip -qq -o "${aflSource}" -d "${_BUILD_DIR}"
}

function build
{
    local installDir=$1
    local buildType=$2
    local buildFlags=$3

    # move to build directory
    cd "${_BUILD_DIR}/AFLplusplus-${_AFL_VERSION}"

    # setup build process
    local aflFlags="AFL_NO_X86=1 STATIC=1 ${buildFlags}"
    local targetDir="${installDir}/${buildType}/"
    if [[ ! -d "${targetDir}" ]];
    then
        mkdir -p ${targetDir}
    fi

    printf "*** Building AFL++ ${_AFL_VERSION} (${buildType}) ***\n"
    env CC=gcc CXX=g++ make distrib ${aflFlags}
    #env CC=clang CXX=clang++ LLVM_CONFIG=llvm-config make distrib ${aflFlags}
    result=$?

    if [[ ${result} -ne 0 ]];
    then
        printf "*** Error! AFL++ could not be compiled correctly. "
        printf "Please check the logs ***\n"
        rm -rf ${_BUILD_DIR}
        exit ${result}
    fi

    printf "*** Installing AFL++ ${_AFL_VERSION} (${buildType}) ***\n"
    cp -P afl-* ${targetDir}
    cp -P lib* ${targetDir}
    cp dynamic_list.txt ${targetDir}
}

function cleanup
{
    printf "*** Removing temporary files ***\n"
    if [[ -d "${_BUILD_DIR}" ]];
    then
        rm -rf ${_BUILD_DIR}
    fi
}


# MAIN SCRIPT
# --------------------------------------------------------------------

if [[ "$#" -ne 1 ]];
then
    printf "*** Error! Incorrect number of arguments ***\n" >&2
    exit 22
fi

installDir="$1/fuzzers/AFL++/"

setup "${installDir}"
# build regular AFL++...
build "${installDir}" "regular" ""
# ...and with sanitizers support
build "${installDir}" "sanitizers" "ASAN_BUILD=1"
cleanup

exit 0