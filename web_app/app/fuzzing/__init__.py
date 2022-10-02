"""
Package that defines the fuzzing logic.

Classes:

    RemoteCommunicationError
    RemoteCommandError
    ProjectDataTransferError
    ProjectNotOwnedError
    ProjectNotFoundError

    CreateProjectForm

    Project
    Fuzzer

    FuzzItAllClient

Functions:

    explore_projects()
    create_project()
    show_project(int)
    download_project(int)
    delete_project(int)
    refresh_project_tasks(int)
    cancel_project_tasks(int)

    ping_repository(str, int) -> bool
    download_repository(str, str, int)
    request_project_creation(int, int, str, str, int, timedelta, int)
    get_project_owned_by_user(int, int) -> Project
    download_project_results(int, int) -> str
    request_project_deletion(int, int)
    refresh_fuzzing_job(int, int)
    cancel_fuzzing_job(int, int)

Misc variables:

    fuzz_bp
"""

from flask import Flask


def init_app(app: Flask):
    '''
    Initializes the fuzzing module inside the Flask application.

       Parameters:
            app(Flask):
                Flask application that will load this module.

        Returns:
            None
    '''
    pass
