#!/bin/bash
######################################################################
#
#   manage_jobs.sh - Bash script to manage the execution of Slurm jobs
#                  launched by FuzzItAll.
#
#   Usage: ./manage_jobs.sh [cancel|refresh]
#
######################################################################

# load context variables
source ../FIA.config


# SCRIPT VARIABLES
# --------------------------------------------------------------------
readonly ACTIVE_JOBS_FILE="${PWD}/../${FIA_ACTIVE_JOBS_FILE}"


# FUNCTIONS
# --------------------------------------------------------------------

function print_usage
{
    printf "$0 - Tool to manage the execution of Slurm jobs launched by FuzzItAll\n"
    printf "Usage: ./$0 [ cancel | refresh ]\n\n"
}

function remove_ended_jobs
{
    if [[ -f "${ACTIVE_JOBS_FILE}" ]];
    then
        local activeJobs="active.lst"
        squeue --noheader --format "%i" > ${activeJobs}
        local endedJobs=$(comm -13 <(sort ${activeJobs}) <(sort ${ACTIVE_JOBS_FILE}))
        # remove ended jobs from the active list (if there are any)...
        if [[ -n ${endedJobs} ]];
        then
            for job in ${endedJobs}
            do
                sed "/${job}/d" ${ACTIVE_JOBS_FILE} > ${ACTIVE_JOBS_FILE}
            done
        fi
        # ... and remove file if its empty
        if [[ -z $(cat "${ACTIVE_JOBS_FILE}") ]];
        then
            rm ${ACTIVE_JOBS_FILE}
        fi
    fi
}

function cancel_all_jobs
{
    # cancel all jobs...
    if [[ -f ${ACTIVE_JOBS_FILE} ]];
    then
        for job in $(cat ${ACTIVE_JOBS_FILE});
        do
            scancel ${job}
        done
    fi

    # ... and remove file
    rm ${ACTIVE_JOBS_FILE}
}


# MAIN SCRIPT
# --------------------------------------------------------------------

case "$1" in
    cancel)
        cancel_all_jobs
        ;;
    refresh)
        remove_ended_jobs
        ;;
    *)
        print_usage
esac

exit 0