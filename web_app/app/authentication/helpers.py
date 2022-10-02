"""
Definition of helper functions for the authentication module.
"""

from datetime import datetime
import flask_login as fl

from app.ext import login_manager
from app.main.models import User

from app.authentication.exceptions import AuthenticationError

# --------------------------------------------------------------------
#   AUTHENTICATION FUNCTIONS
# --------------------------------------------------------------------


def login_to_service(username: str, password: str,
                     remember: bool = False) -> None:
    """
    Attemps to log in a given user to the web service.

        Parameters:
            username (str):
                Name identifying the user in the service.
            password (str):
                Password to protect the user's identity.
            remember (bool):
                Whether or not remember the user's session cookie.

        Raises:
            app.authentication.exceptions.AuthenticationError -- Either\
                the user is not active, does not exist or the password\
                is wrong.
    """
    user = User.get_by_username(username)
    if user is not None and user.check_password(password):
        if not fl.login_user(user, remember=remember):
            raise AuthenticationError(
                'User is no longer active in the system.')

        # update last login date
        user.last_login = datetime.now()
        user.save()

    else:
        raise AuthenticationError(
            'User does not exist or invalid password.')


# --------------------------------------------------------------------
#   OTHER FUNCTIONS
# --------------------------------------------------------------------


@login_manager.user_loader
def load_user(user_id: int):
    '''
    Decorator function of 'flask_login' to manage user logins.

        Parameters:
            user_id (int):
                Identifier of the user.

        Returns:
            (User):
                Database model representing a user.
    '''
    return User.get_by_id(user_id)
