"""
Package that defines the authentication logic.

Classes:

    AuthenticationError
    RemoteCommunicationError
    RemoteCommandError
    DataTransferError

    LoginForm

    RemoteClient

Functions:

    init_app(Flask)

    login_to_fia_web_service(str, str, bool)
    load_user(int)

    login()
    logout()

Misc variables:

    logger
    auth_bp
"""

from flask import Flask


def init_app(app: Flask):
    '''
    Initializes the authentication module inside the Flask application.

       Parameters:
            app(flask.Flask):
                Flask application that will load this module.

        Returns:
            None
    '''
    pass
