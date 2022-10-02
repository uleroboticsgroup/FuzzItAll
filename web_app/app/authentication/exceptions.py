"""
Definition of exceptions related to the authentication module.
"""

from app.main.exceptions import FuzzItAllException


class AuthenticationError(FuzzItAllException):
    """
    User failed to authenticate on some system.
    """
    pass


class RemoteCommunicationError(FuzzItAllException):
    """
    Failed to create or establish communication with a remote system.
    """
    pass


class RemoteCommandError(FuzzItAllException):
    """
    Failed to execute a command on a remote system.
    """
    pass


class DataTransferError(FuzzItAllException):
    """
    Failed to download or upload data between remote host and localhost.
    """
    pass
