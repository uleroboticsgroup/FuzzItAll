"""
Definition of exceptions related to the main module.
"""


class FuzzItAllException(Exception):
    """
    Generic exception produced inside the FuzzItAll platform.
    """
    pass


class FuzzItAllFatalError(FuzzItAllException):
    """
    Fatal error forcing to stop the operation in progress.
    """
    pass


class FuzzItAllItemNotFoundError(FuzzItAllException):
    """
    Generic error occurred when an element has not been found in the database.
    """
    pass
