"""
Definition of exceptions related to the user module.
"""

from app.main.exceptions import FuzzItAllItemNotFoundError


class UserNotFoundError(FuzzItAllItemNotFoundError):
    """
    Requested user does not exist.
    """
    pass


class HPCSystemNotFoundError(FuzzItAllItemNotFoundError):
    """
    Requested HPC system does not exist.
    """
    pass
