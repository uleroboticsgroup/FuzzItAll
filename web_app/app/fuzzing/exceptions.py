"""
Definition of exceptions related to the fuzzing module.
"""

from app.main.exceptions import FuzzItAllException, FuzzItAllItemNotFoundError


class ProjectNotOwnedError(FuzzItAllException):
    """
    Requested project is not owned by the given user.
    """
    pass


class ProjectNotFoundError(FuzzItAllItemNotFoundError):
    """
    Requested project does not exist.
    """
    pass
