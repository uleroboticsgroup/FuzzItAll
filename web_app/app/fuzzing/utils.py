"""
Definition of utils for the fuzzing module.
"""

import logging

from pathlib import PurePosixPath

from datetime import datetime, timedelta

from app.main.exceptions import FuzzItAllException

from app.authentication.utils import RemoteClient
from app.authentication.exceptions import DataTransferError, RemoteCommandError

from app.main.models import HPCSystem

from app.fuzzing.models import (
    Project, FuzzingJob, SlurmJobState
)


def slurm_format_time(duration: timedelta) -> str:
    '''
    Formats a timedelta duration to Slurm's days-hours:minutes format.

        Parameters:
            duration (timedelta):
                Duration of time to be formatted.

        Returns:
            time_fmt (str):
                Duration in Slurm's days-hours:minutes format.

        Raises:
            None
    '''
    SECS_IN_DAY = 86400
    SECS_IN_HOUR = 3600
    SECS_IN_MIN = 60

    # convert seconds into days, hours and minutes
    seconds = int(duration.total_seconds())
    days, seconds = divmod(seconds, SECS_IN_DAY)
    hours, seconds = divmod(seconds, SECS_IN_HOUR)
    minutes, seconds = divmod(seconds, SECS_IN_MIN)

    time_fmt = f"{hours:02d}:{minutes:02d}"
    if days > 0:
        time_fmt = f"{days}-{time_fmt}"

    return time_fmt


class FuzzItAllClient:
    """
    Client to interact with a remote HPC system containing the FuzzItAll
    command line tool.

    Attributes
    ----------
    __WORKSPACE : str
        Path, in the HPC system, to the FuzzItAll workspace.
    __ROOT : str
        Path, in the HPC system, to the root directory of FuzzItAll.
    FIA_PROJECT_CFG_FILE : str
        Name of the configuration file required for a repository to be\
        compatible with FuzzItAll.

    Methods
    -------
    get_fuzzers() -> list:
        Obtains a list of the fuzzing engines available in the HPC system.
    get_max_parallel_tasks() -> int:
        Obtains the maximum number of parallel fuzzing tasks per project.
    __get_workspace_path(str) -> str:
        Obtains the remote path where the data of a given project is stored.

    upload(str, str):
        Uploads a locally stored repository to the FuzzItAll workspace.
    submit(Project, str, int, timedelta) -> int
        Submits a project to the HPC system in order to fuzz its target.
    delete(Project):
        Deletes a project from the FuzzItAll workspace.
    update(FuzzingJob):
        Updates the status of a fuzzing job.
    cancel(FuzzingJob):
        Cancels the execution of a fuzzing job.
    pause(FuzzingJob):
        Pauses the execution of a fuzzing job.
    resume(FuzzingJob):
        Continues the execution of a fuzzing job.
    """

    FIA_PROJECT_CFG_FILE = 'fia_project.conf'

    def __init__(self, hpcs: HPCSystem):
        """
        Default constructor.

        Parameters
        ----------
        hpcs : HPCSystem
            HPC system containing the FuzzItAll command line tool.

        Raises
        ------
        AuthenticationError -- Failed to authenticate on the HPC system.\\
        RemoteCommunicationError -- Either failed to connect/establish a\
                                    connection to the HPC system or host\
                                    SSH key did not match.\\
        FuzzItAllException -- FuzzItAll not properly installed in the\
                              HPC system.
        """
        self.__logger = logging.getLogger('app.fuzzing.routes')

        # establish connection with the HPC system
        self.__hpcs_client = RemoteClient(
            hpcs.host, hpcs.port, hpcs.user, hpcs.password)

        # and check that FuzzItAll is installed on the HPC system by retrieving
        # its environment variables
        get_vars_cmd = 'echo $FIA_ROOT; echo $FIA_WORKSPACE'
        try:
            get_vars_out = self.__hpcs_client.run(get_vars_cmd)
            if (get_vars_out['exit_code'] == 0
                    and len(get_vars_out['output']) == 2):
                self.__ROOT, self.__WORKSPACE = get_vars_out['output']
            else:
                msg = 'Either one or both FuzzItAll environment variables does not exist.'
                self.__logger.error(f'[FuzzItAllClient] {msg}')
                raise FuzzItAllException(msg)
        except FuzzItAllException as e:
            msg = 'FuzzItAll is not properly installed on remote host.'
            self.__logger.error(f'[FuzzItAllClient] {msg}. Reason: {e}')
            raise FuzzItAllException(msg)

    # ----------------------------------------------------------------
    #   SUPPORT FOR "WITH" STATEMENT
    # ----------------------------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.__hpcs_client.disconnect()

    # ----------------------------------------------------------------
    #   FUZZITALL CLI TOOL VARIABLE ACCESSOR METHODS
    # ----------------------------------------------------------------

    def get_fuzzers(self) -> list:
        """
        Obtains a list of the fuzzing engines available in the HPC system.

        Returns
        -------
        engines : list
            List with the names of all the fuzzers available in the HPC system.

        Raises
        ------
        FuzzItAllException -- Failed to get the list of fuzzing engines\
                              available.
        """
        get_fuzzers_cmd = f'ls {self.__ROOT}fuzzer/'

        # get the list of fuzzing engines
        try:
            get_fuzzers_out = self.__hpcs_client.run(get_fuzzers_cmd)
            engines = get_fuzzers_out['output'] if (
                get_fuzzers_out['exit_code'] == 0) else None
            return engines
        except RemoteCommandError as e:
            raise FuzzItAllException(f'[FuzzItAllClient]\
                Failed to get the list of available fuzzing engines.') from e

    def get_max_parallel_tasks(self) -> int:
        """
        Obtains the maximum number of parallel fuzzing tasks per project.

        Returns
        -------
        max_tasks : int
            Maximum number of parallel fuzzing tasks that a project can run
            or -1 if this number is not available.

        Raises
        ------
        FuzzItAllException -- Failed to get the maximum number of parallel\
                              tasks.
        """
        get_tasks_cmd = f'cat {self.__ROOT}FIA.config \
                            | egrep \'FIA_MAX_PARALLEL_FUZZERS=[0-9]+\' \
                            | cut -d = -f2'

        # get the maximum number of tasks
        try:
            get_tasks_out = self.__hpcs_client.run(get_tasks_cmd)
            max_tasks = int(get_tasks_out['output'][0]) if (
                get_tasks_out['exit_code'] == 0) else -1
            return max_tasks
        except RemoteCommandError as e:
            msg = 'Failed to get the maximum number of parallel tasks.'
            self.__logger.error(f'[FuzzItAllClient] {msg}. Reason: {e}')
            raise FuzzItAllException(msg)

    def get_max_wall_time(self) -> int:
        """
        TODO (gonestco): description
        """
        return 3

    def __get_workspace_path(self, project_name: str) -> str:
        """
        Obtains the remote path where the data of a given project is stored.

        Returns
        -------
        PurePosixPath (str):
            Remote path where the repository is stored.
        """
        return PurePosixPath(self.__WORKSPACE, project_name).as_posix()

    # ----------------------------------------------------------------
    #   PROJECT RELATED METHODS
    # ----------------------------------------------------------------

    def upload(self, project_name: str, local_path: str):
        """
        Uploads a locally stored repository to the FuzzItAll workspace.

        Parameters
        ----------
        project_name : str
            Project alias.
        local_path : str
            Path to the repository to retrieve from localhost.

        Returns
        -------
        None

        Raises
        ------
        DataTransferError -- Project upload failed.
        """
        remote_path = self.__get_workspace_path(project_name)

        # upload the repository
        try:
            self.__hpcs_client.upload_data(local_path, remote_path)
        except DataTransferError as e:
            raise DataTransferError(f'[FuzzItAllClient]\
                Failed to upload the project.') from e

    def submit(self, project: Project, fuzzer: str, num_tasks: int,
               wall_time: timedelta) -> int:
        """
        Submits a project to the HPC system in order fuzz its target.

        Parameters
        ----------
        project_name : str
            Project alias.
        repo_path : str
            Path where the project source code is stored locally.
        fuzzer : str
            Name of the fuzzer that will execute the fuzzing tasks.
        num_tasks : int
            Number of parallel tasks to be used during the fuzzing process.
        wall_time : str
            Time during which to run fuzzing tasks on the HPC system.

        Returns
        -------
        job_id : int
            Job identifier from the Slurm Workload Manager.

        Raises
        ------
        FuzzItAllException -- FuzzItAll execution failed.
        """
        project_path = self.__get_workspace_path(project.name)
        job_duration = slurm_format_time(wall_time)
        submit_cmd = f'{self.__ROOT}fuzzitall \
                        -p {project_path} -f {fuzzer} \
                        -n {num_tasks} -t {job_duration}'

        # submit the project
        try:
            submit_out = self.__hpcs_client.run(submit_cmd)
            if (submit_out['exit_code'] == 0):
                job_id = int(submit_out['output'].pop())
                return job_id
            else:
                raise FuzzItAllException(submit_out['error'])
        except FuzzItAllException as e:
            raise FuzzItAllException(f'[FuzzItAllClient]\
                Failed to submit the project to the HPC system.') from e

    def delete(self, project: Project):
        """
        Deletes a project from the FuzzItAll workspace.

        Parameters
        ----------
        project : Project
            Project which is going to be deleted.

        Returns
        -------
        None

        Raises
        ------
        FuzzItAllException -- Failed to delete the project.
        """
        project_path = self.__get_workspace_path(project.name)
        delete_cmd = f'rm -rf {project_path}'

        # delete the project
        try:
            delete_out = self.__hpcs_client.run(delete_cmd)
            if (delete_out['exit_code'] == 1):
                raise FuzzItAllException(delete_out['error'])
        except FuzzItAllException as e:
            raise FuzzItAllException(f'[FuzzItAllClient]\
                Failed to delete the project.') from e

    # ----------------------------------------------------------------
    #   FUZZING JOB RELATED METHODS
    # ----------------------------------------------------------------

    def update(self, fuzz_job: FuzzingJob):
        """
        Updates the status of a fuzzing job.

        Parameters
        ----------
        fuzz_job : FuzzingJob
            Fuzzing job to update.

        Returns
        -------
        None

        Raises
        ------
        FuzzItAllException -- Failed to update the fuzzing job status.
        """
        update_cmd = f"sacct -j {fuzz_job.job_id} \
                              --format=JobName,State,Elapsed \
                              | egrep FuzzItAll | head -n 1 \
                              | xargs | cut -d ' ' -f2,3 | tr ' ' '\n'"

        # get current status of the job and then update its db entry
        try:
            update_out = self.__hpcs_client.run(update_cmd)
            if (update_out['exit_code'] != 0):
                raise FuzzItAllException(update_out['error'])
        except FuzzItAllException as e:
            raise FuzzItAllException(f'[FuzzItAllClient]\
                Failed to update fuzzing job status.') from e

        # elapsed time has the DAYS-HOURS:MINUTES:SECONDS format
        status = update_out['output']
        elapsed_time = status.pop().split('-')
        et_hhmmss = datetime.strptime(elapsed_time.pop(), "%H:%M:%S")
        et_dd = float(elapsed_time.pop()) if (elapsed_time) else 0.0
        fuzz_job.elapsed_time = timedelta(
            days=et_dd, hours=et_hhmmss.hour, minutes=et_hhmmss.minute,
            seconds=et_hhmmss.second).total_seconds()

        state = status.pop().replace('+', '')
        if (fuzz_job.state.name != state):
            fuzz_job.state = SlurmJobState[state]

        fuzz_job.save()

    def cancel(self, fuzz_job: FuzzingJob):
        """
        Cancels the execution of a fuzzing job.

        Parameters
        ----------
        fuzz_job : FuzzingJob
            Fuzzing job to cancel.

        Returns
        -------
        None

        Raises
        ------
        FuzzItAllException -- Failed to cancel the fuzzing job execution.
        """
        cancel_cmd = f'scancel {fuzz_job.job_id}'

        # cancel the job
        try:
            cancel_out = self.__hpcs_client.run(cancel_cmd)
            if (cancel_out['exit_code'] != 0):
                raise FuzzItAllException(cancel_out["error"])
        except FuzzItAllException as e:
            raise FuzzItAllException(f'[FuzzItAllClient]\
                Failed to cancel fuzzing job.') from e

    def pause(self, fuzz_job: FuzzingJob):
        """
        Pauses the execution of a fuzzing job.

        Parameters
        ----------
        fuzz_job : FuzzingJob
            Fuzzing job to cancel.

        Returns
        -------
        None

        Raises
        ------
        FuzzItAllException -- Failed to pause the fuzzing tasks.
        """
        pause_cmd = f'scontrol suspend {fuzz_job.job_id}'

        # pause the job
        try:
            pause_out = self.__hpcs_client.run(pause_cmd)
            if (pause_out['exit_code'] != 0):
                raise FuzzItAllException(pause_out['error'])
        except FuzzItAllException as e:
            raise FuzzItAllException(f'[FuzzItAllClient]\
                Failed to pause the fuzzing job.') from e

    def resume(self, fuzz_job: FuzzingJob):
        """
        Continues the execution of a fuzzing job.

        Parameters
        ----------
        fuzz_job : FuzzingJob
            Fuzzing job to be resumed.

        Returns
        -------
        None

        Raises
        ------
        FuzzItAllException -- Failed to resume the project.
        """
        resume_cmd = f'scontrol resume {fuzz_job.job_id}'

        # resume the job
        try:
            resume_out = self.__hpcs_client.run(resume_cmd)
            if (resume_out['exit_code'] != 0):
                raise FuzzItAllException(resume_out['error'])
        except FuzzItAllException as e:
            raise FuzzItAllException(f'[FuzzItAllClient]\
                Failed to resume the fuzzing job') from e

    def download(self, project_name: str, local_path: str):
        """
        Downloads the fuzzing results of the project.

        Parameters
        ----------
        project_name : str
            Project alias.
        local_path : str
            Path in which to receive files locally.

        Returns
        -------
        None

        Raises
        ------
        DataTransferError -- Project results download failed.
        """
        remote_path = f'{self.__get_workspace_path(project_name)}/fuzz-out'

        # download the project results
        try:
            self.__hpcs_client.download_data(remote_path, local_path)
        except DataTransferError as e:
            raise DataTransferError(f'[FuzzItAllClient]\
                Failed to download the project results.') from e

    def get_stats(self, project: Project):
        """
        TODO: description
        """
        remote_path = self.__get_workspace_path(project.name)
        get_stats_cmd = f'{self.__ROOT}utils/monitor-fuzzing -p {remote_path} -f AFL++'
        stdout = self.__hpcs_client.run(get_stats_cmd)['output']
        return stdout
