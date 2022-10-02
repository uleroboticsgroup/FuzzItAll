"""
Definition of helper functions for the administration module.
"""

from functools import wraps as ft_wraps
from flask_login import current_user as fl_current_user
from werkzeug.security import generate_password_hash as ws_generate_password_hash
from flask import current_app as fl_current_app

from app.main.models import HPCSystem, User
from app.main.exceptions import FuzzItAllFatalError
from app.fuzzing.utils import FuzzItAllClient
import app.administration.exceptions as fia_ade


# --------------------------------------------------------------------
#   USER CRUD FUNCTIONS
# --------------------------------------------------------------------


def create_user(username: str, password: str, admin: bool) -> None:
    '''
    Creates a new user in the database.

        Parameters:
            username (str):
                Name identifying the user in the system.
            password (str):
                Password (plain text) to protect the user's identity.
            admin (bool):
                Whether the user has admin permissions or not.

        Returns:
            None
    '''
    user = User(username=username,
                password=ws_generate_password_hash(password),
                admin=admin)
    user.save()


def update_user(user_id: int, password: str) -> None:
    '''
    Updates the user data (currently only the password).

        Parameters:
            user_id (int):
                Internal user identifier.
            password (str):
                Password to protect the user's identity.

        Returns:
            None

        Raises:
            UserNotFoundError -- Given user does not exist in the system.
    '''
    user = User.get_by_id(user_id)
    if user is None:
        raise fia_ade.UserNotFoundError

    # update password if it is different from the current one
    if not user.check_password(password):
        user.password = ws_generate_password_hash(password)
        user.save()


def delete_user(user_id: int) -> None:
    '''
    Deletes a user from the database.

        Parameters:
            user_id (int):
                Internal user identifier.

        Returns:
            None

        Raises:
            UserNotFoundError -- Given user does not exist in the system.
    '''
    user = User.get_by_id(user_id)
    if user is None:
        raise fia_ade.UserNotFoundError

    user.delete()


# --------------------------------------------------------------------
#   HPC SYSTEM CRUD FUNCTIONS
# --------------------------------------------------------------------


def create_hpcs(name: str, host: str, port: int, user: str,
                password: str, ssh_key: str) -> None:
    '''
    Creates a new HPC system in the database.

        Parameters:
            name (str):
                Name of the remote HPC system.
            host (str):
                Name or IP address of the remote HPC system.
            port (str):
                Port enabled on host for SSH connection.
            user (str):
                Username for the SSH connection.
            password (str):
                Password for username or passphrase for SSH key.
            ssh_key (str):
                SSH key for connecting to the remote HPC system.

        Returns:
            None
    '''
    hpcs = HPCSystem(name=name, host=host, port=port,
                     user=user, password=password)
    with FuzzItAllClient(hpcs) as fia_client:
        hpcs.max_wall_time = fia_client.get_max_wall_time()
        hpcs.max_tasks = fia_client.get_max_parallel_tasks()

    hpcs.save()


def delete_hpcs(hpcs_id: int) -> None:
    '''
    Deletes a HPC system from the database.

        Parameters:
            hpcs_id (int):
                Internal HPC system identifier.

        Returns:
            None

        Raises:
            HPCSystemNotFoundError -- Given HPC system does not exist\
                                      in the system.
    '''
    hpcs = HPCSystem.get_by_id(hpcs_id)
    if hpcs is None:
        raise fia_ade.HPCSystemNotFoundError

    hpcs.delete()


# --------------------------------------------------------------------
#   OTHER FUNCTIONS
# --------------------------------------------------------------------


def admin_required(f):
    '''
    Decorator function that restrict access to a route to only those users
    who have administration permissions.

        Parameters:
            f (function):
                Function to be decorated.

        Returns:
            (decorated_function):
                Decorated function to require administrator permissions.
    '''
    @ft_wraps(f)
    def decorated_function(*args, **kwargs):
        if not fl_current_user.admin:
            raise FuzzItAllFatalError(
                'You are not allowed to perform this operation.')
        return f(*args, **kwargs)
    return decorated_function


def save_system_settings(items_pp: int) -> None:
    '''
    Saves the system settings.

        Parameters:
            items_pp (int):
                Items per page setting.

        Returns:
            None
    '''
    fl_current_app.config.update(
        ITEMS_PER_PAGE=items_pp
    )
