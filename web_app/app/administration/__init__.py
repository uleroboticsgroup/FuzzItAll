"""
Package that defines the administration functionality of the application.

Classes:

    UserNotFoundError
    HPCSystemNotFoundError

    CreateUserForm
    ChangePasswordForm
    CreateHPCSystemForm
    EditSystemSettingsForm

Functions:

    init_app(flask.Flask)
    create_admin_cmd(str, str)

    create_user(str, str, bool)
    update_user(int, str)
    delete_user(int)
    create_hpcs(str, str, int, str, str)
    delete_hpcs()
    admin_required(function)
    save_system_settings(int)

    browse_users()
    create_user()
    update_user(int)
    delete_user(int)
    browse_hpcs()
    create_hpcs()
    delete_hpcs(int)
    browse_system()
    download_system_log()

Misc variables:

    logger
    admin_bp
"""

from flask import Flask
from flask.cli import with_appcontext as fc_with_appcontext
import click


def init_app(app: Flask):
    '''
    Initializes the administration module inside the Flask application.

        Parameters:
            app (flask.Flask):
                Flask application that will load this module.

        Returns:
            None
    '''
    app.cli.add_command(create_admin_cmd)


@click.command('create-admin')
@click.option('--username', default='admin')
@click.password_option()
@fc_with_appcontext
def create_admin_cmd(username: str, password: str):
    '''
    Create an administrator user.
    '''
    from app.administration.helpers import create_user as fia_adh_create_user
    fia_adh_create_user(username=username, password=password, admin=True)
    click.echo('Administration user created successfully.')
