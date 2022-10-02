"""
Package that defines the registration logic.

Classes:

Functions:

    init_app(Flask)

Misc variables:

    reg_bp
"""

from flask import Flask


def init_app(app: Flask):
    '''
    Initializes the registration module inside the Flask application.

       Parameters:
            app(flask.Flask):
                Flask application that will load this module.

        Returns:
            None
    '''
    pass

    @app.context_processor
    def inject_template_scope():
        '''
        TODO (gonestco): description
        '''
        injections = dict()

        def cookies_check():
            from flask import request
            value = request.cookies.get('cookie_consent')
            return value == 'true'
        injections.update(cookies_check=cookies_check)

        return injections
