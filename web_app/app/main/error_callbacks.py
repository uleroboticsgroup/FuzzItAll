"""
Definition of error callbacks related to the main module.
"""

from flask import render_template


def fia_fatal_error_callback(msg: str):
    '''
    Displays the error page after a fatal error has occurred in the
    application.

        Parameters:
            msg (str):
                Error message to display.

        Returns:
            render_template (str):
                HTML code to render the error page.
    '''
    template_context = dict(error='Internal Error', message=msg)
    return render_template('error.html', **template_context), 500


def fia_not_found_error_callback(msg: str):
    '''
    Displays the error page after a not found error has occurred in the
    application.

        Parameters:
            msg (str):
                Error message to display.

        Returns:
            render_template (str):
                HTML code to render the error page.
    '''
    template_context = dict(error='Not Found', message=msg)
    return render_template('error.html', **template_context), 404
