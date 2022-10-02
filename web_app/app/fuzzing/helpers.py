"""
Definition of helper functions for the fuzzing module.
"""

from flask import current_app

from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import make_archive, move
from requests import get, exceptions
from datetime import datetime, timedelta

from git import Repo
from git.exc import GitCommandError

from app.main.exceptions import FuzzItAllException

from app.main.models import HPCSystem, User
from app.fuzzing.models import Project, FuzzingJob
from app.fuzzing.exceptions import (
    ProjectNotFoundError, ProjectNotOwnedError
)
from app.fuzzing.utils import FuzzItAllClient
from app.authentication.exceptions import DataTransferError


def ping_repository(repo_url: str, token_id: int = None) -> bool:
    '''
    Pings a repository URL.

        Parameters:
            repo_url (str):
                Repository URL.
            token_id (int):
                Optional identifier of the token that allows access to\
                the URL.

        Returns:
            valid_ping (bool):
                Whether the repository exists or not.

        Raises:
            None
    '''
    valid_ping = False
    try:
        # TODO (gonestco): review SSL verification!!
        get(repo_url, verify=True)
        valid_ping = True
    except (exceptions.ConnectionError, exceptions.SSLError):
        # ignore any exceptions
        pass

    return valid_ping


def download_repository(repo_url: str, target_path: str, token_id: int = None):
    '''
    Downloads the source code of a project to the target path.
    IMPORTANT: Only public Git repository URLs are currently supported.

        Parameters:
            repo_url (str):
                URL of the repository.
            target_path (str):
                Local destination path where to download the repository.
            token_id (int):
                Optional identifier of the token that allows access to\
                the repository.

        Returns:
            None

        Raises:
            FuzzItAllException -- Repository type not supported or not\
                                  compatible with FuzzItAll.\\
            ProjectDataTransferError -- Failed to download the repository.
    '''
    src_dir = Path(target_path, 'src')

    # TODO (gonestco): download repository depending on repository type
    # TODO (gonestco): add support for token authentication
    try:
        if repo_url.endswith('.git'):
            Repo.clone_from(url=repo_url, to_path=src_dir)
        else:
            raise FuzzItAllException('Repository type not supported.')
    except GitCommandError:
        raise DataTransferError('Failed to download repository.')

    # check if the repository is compatible with FuzzItAll
    if not Path(src_dir, FuzzItAllClient.FIA_PROJECT_CFG_FILE).exists():
        raise FuzzItAllException(
            'Given repository does not support FuzzItAll.')


def create_project(user_id: int, hpcs_id: int, name: str, url: str,
                   num_tasks: int, wall_time: timedelta, token_id: int = None):
    '''
    Creates a new project by requesting its execution to a HPC system.

        Parameters:
            user_id (int):
                Identifier of the user that will own the project.
            hpcs_id (int):
                HPC system where the project will be requested to run.
            name (str):
                Alias of the project.
            url (str):
                URL of the repository containing the sources of the project.
            num_tasks (int):
                Number of parallel tasks to be used during the fuzzing process.
            wall_time (timedelta):
                Wall time during which to run fuzzing tasks on the HPC system.
            token_id (int):
                Optional identifier of the token that allows access to\
                the repository URL.

        Returns:
            None

        Raises:
            FuzzItAllException -- Request was unsuccessful.
    '''
    current_date = datetime.now()
    project = Project(user_id=user_id, created=current_date,
                      last_update=current_date, name=name, url=url,
                      hpcs_id=hpcs_id)
    hpcs = HPCSystem.get_by_id(hpcs_id)

    try:
        with TemporaryDirectory(dir=current_app.config['TMP_DIR']) as tmp_dir:
            # first download the repository locally
            repo_path = Path(tmp_dir)
            download_repository(project.url, repo_path)

            with FuzzItAllClient(hpcs) as fia_client:
                # then upload it to FuzzItAll
                fia_client.upload(project.name, repo_path)

                # and request its creation
                job_id = fia_client.submit(
                    project, 'AFL++', num_tasks, wall_time)
                if job_id is not None:
                    project.save()
                    fuzz_job = FuzzingJob(job_id=job_id,
                                          project_id=project.id,
                                          num_tasks=num_tasks,
                                          wall_time=wall_time.total_seconds())
                    fuzz_job.save()

    except (PermissionError, DataTransferError, FuzzItAllException) as e:
        raise FuzzItAllException(f'There was an error in requesting the\
            creation of the project. {e}') from e


def get_project_owned_by_user(project_id: int, user: User) -> Project:
    '''
    Obtains the data of a project owned by some user.

        Parameters:
            project_id (int):
                Identifier of the project.
            user_id (int):
                Identifier of the presumed user owning the project.

        Returns:
            project (Project):
                Project data.

        Raises:
            ProjectNotFoundError -- Project identifier does not exist.\\
            ProjectNotOwnedError -- Project exists but the user is not\
                                    its owner.
    '''
    project = Project.get_by_id(project_id)
    if project is None:
        raise ProjectNotFoundError
    elif not user.admin and project.user_id != user.id:
        raise ProjectNotOwnedError
    else:
        return project


def download_project_results(project_id: int, user_id: int) -> str:
    '''
    Downloads fuzzing results for a given project.

        Parameters:
            project_id (int):
                Identifier of the project.
            user_id (int):
                Identifier of the user owning the project.

        Returns:
            results (str):
                Path to the archive file containing the fuzzing results.

        Raises:
            ProjectDownloadError -- Results download was unsuccessful.
            TODO (gonestco): FuzzItAllException --
    '''
    project = get_project_owned_by_user(project_id, user_id)
    hpcs = HPCSystem.get_by_id(project.hpcs_id)
    results = Path(current_app.config['TMP_DIR'], f'{project.name}.zip')

    # if project results are not in cache, connect to the HPC system and
    # download them
    if not results.exists():
        try:
            with TemporaryDirectory(dir=current_app.config['TMP_DIR']) as tmp_dir:
                repo_path = Path(tmp_dir)

                with FuzzItAllClient(hpcs) as fia_client:
                    fia_client.download(project.name, repo_path)
                    tmp_results = make_archive(
                        base_name=project.name, format='zip', root_dir=repo_path
                    )
                    results = move(tmp_results, current_app.config['TMP_DIR'])
        except PermissionError:
            raise FuzzItAllException
    else:
        results = results.as_posix()

    return results


def request_project_deletion(project_id: int, user_id: int):
    '''
    Deletes a certain project.

        Parameters:
            project_id (int):
                Identifier of the project.
            user_id (int):
                Identifier of the user owning the project.

        Returns:
            None

        Raises:
            TODO: description.
    '''
    project = get_project_owned_by_user(project_id, user_id)
    hpcs = HPCSystem.get_by_id(project.hpcs_id)

    # delete content from the HPC
    with FuzzItAllClient(hpcs) as hpcs_conn:
        hpcs_conn.cancel(project.jobs[0])
        hpcs_conn.delete(project)

    # then delete from db
    project.delete()


def refresh_fuzzing_job(project_id: int, user_id: int):
    '''
    TODO (gonestco): description
    '''
    project = get_project_owned_by_user(project_id, user_id)
    hpcs = HPCSystem.get_by_id(project.hpcs_id)

    # update fuzzing job and project
    with FuzzItAllClient(hpcs) as hpcs_conn:
        hpcs_conn.update(project.jobs[0])
        project.update_project_state()
        project.last_update = datetime.now()
        project.save()


def cancel_fuzzing_job(project_id: int, user_id: int):
    '''
    TODO (gonestco): description
    '''
    project = get_project_owned_by_user(project_id, user_id)
    hpcs = HPCSystem.get_by_id(project.hpcs_id)

    with FuzzItAllClient(hpcs) as hpcs_conn:
        hpcs_conn.cancel(project.jobs[0])
