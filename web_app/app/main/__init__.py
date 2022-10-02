"""
Package that defines the core functionality of the application.

Classes:

    FuzzItAllException
    FuzzItAllFatalError
    FuzzItAllItemNotFoundError

    User
    HPCSystem

Functions:

    init_app(Flask)
    _set_error_handlers_callbacks(Flask)
    create_db_cmd()

    fia_fatal_error_callback(str)
    fia_not_found_error_callback(str)

    get_pagination_params(WSGIMultiDict[str, str], str) -> tuple

    index()
    help()
    dashboard()

Misc variables:

    main_bp
"""

from flask import Flask
from flask.cli import with_appcontext as fc_with_appcontext
import click

import app.main.exceptions as fia_me
import app.main.error_callbacks as fia_mecb


def init_app(app: Flask) -> None:
    '''
    Initializes the main module inside the Flask application.

        Parameters:
            app (Flask):
                Flask application that will load this module.

        Returns:
            None
    '''
    _set_error_handlers_callbacks(app)
    app.cli.add_command(create_db_cmd)


def _set_error_handlers_callbacks(app: Flask) -> None:
    '''
    Defines the handlers in charge of managing errors related to the module's
    functionality by decorating the given Flask application.

        Parameters:
            app (Flask):
                Flask application that will be decorated with the error\
                handlers.

        Returns:
            None
    '''

    @app.errorhandler(fia_me.FuzzItAllFatalError)
    def handle_fia_fatal_error(e):
        return fia_mecb.fia_fatal_error_callback(str(e))

    @app.errorhandler(fia_me.FuzzItAllItemNotFoundError)
    def handle_fia_not_found_error(e):
        return fia_mecb.fia_not_found_error_callback(str(e))

    @app.errorhandler(500)
    def handle_internal_error(e):
        return fia_mecb.fia_fatal_error_callback(str(e))

    @app.errorhandler(404)
    def handle_url_not_found(e):
        return fia_mecb.fia_not_found_error_callback(str(e))


@click.command('create-db')
@fc_with_appcontext
def create_db_cmd():
    '''
    Creates the FuzzItAll database.
    '''
    from app.db import db
    db.create_all()
    click.echo('FuzzItAll database created successfully.')
