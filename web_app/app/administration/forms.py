"""
Definition of forms related to the administration module.
"""

from flask_wtf import FlaskForm
import wtforms as wtf
import wtforms.validators as wtfv
from flask.config import Config as FlaskConfig

import app.main.models as fia_mm


class CreateUserForm(FlaskForm):
    """
    Form to define the creation of a new user.

    Attributes
    ----------
    submit : wtforms.SubmitField
        Submit button.
    username : wtforms.StringField
        Name identifying the user in the service.
    password : wtforms.PasswordField
        Password to protect the user's identity.
    confirm : wtforms.PasswordField
        Password confirmation.
    admin : wtforms.BooleanField
        Whether the user has administration permissions or not.

    Methods
    -------
    validate_username(flask_wtf.FlaskForm, wtforms.StringField):
        Checks that the username given to the user does not already exist
        in the database.
    """
    submit = wtf.SubmitField('Create')
    # user credentials
    username = wtf.StringField('Username', validators=[wtfv.InputRequired()])
    password = wtf.PasswordField('Password', validators=[
        wtfv.InputRequired(),
        wtfv.EqualTo('confirm', message='Passwords must match')])
    confirm = wtf.PasswordField(
        'Confirm password', validators=[wtfv.InputRequired()])
    # role
    admin = wtf.BooleanField('Administrator')

    def to_dict(self) -> dict:
        data = dict(
            username=self.username.data,
            password=self.password.data,
            admin=self.admin.data
        )
        return data

    def validate_username(form: FlaskForm, field: wtf.StringField):
        """
        Checks that the username given to the user does not already exist
        in the system.

        Parameters
        ----------
        form : flask_wtf.FlaskForm
            Form containing the 'username' field.
        field : wtforms.StringField
            'username' field to validate.

        Returns
        -------
        None

        Raises
        ------
        wtforms.validators.ValidationError -- A user exists with that\
                                              username.
        """
        user = fia_mm.User.get_by_username(field.data)
        if user is not None:
            raise wtfv.ValidationError(
                'A user with this name already exists in the system. '
                'Please use a different one.')


class ChangePasswordForm(FlaskForm):
    """
    Form to define the change of password of a user.

    Attributes
    ----------
    submit : wtforms.SubmitField
        Submit button.
    new_password : wtforms.PasswordField
        New password to protect the user's identity.
    confirm : wtforms.PasswordField
        New password confirmation.
    """
    submit = wtf.SubmitField('Update')
    # password
    new_password = wtf.PasswordField(
        'New Password', validators=[wtfv.InputRequired()])
    confirm = wtf.PasswordField('Confirm Password', validators=[
        wtfv.InputRequired(),
        wtfv.EqualTo('new_password', message='Passwords must match')])

    def to_dict(self) -> dict:
        data = dict(password=self.new_password.data)
        return data


class CreateHPCSystemForm(FlaskForm):
    """
    Form to define the creation of a new HPC system.

    Attributes
    ----------
    submit : wtforms.SubmitField
        Submit button.
    name : wtforms.StringField
        Name of the remote HPC system.
    host : wtforms.StringField
        Name or IP address of the remote HPC system.
    port : wtforms.IntegerField
        Port enabled on host for SSH connection.
    user : wtforms.StringField
        Username for the SSH connection.
    password : wtforms.PasswordField
        Password for username or passphrase for SSH key.

    Methods
    -------
    validate_name(flask_wtf.FlaskForm, wtforms.StringField):
        Checks that the name given to the HPC system does not already
        exist in the database.
    """
    submit = wtf.SubmitField('Create')
    # identification
    name = wtf.StringField('Name', validators=[wtfv.InputRequired()])
    # connection details
    host = wtf.StringField('Host', validators=[wtfv.InputRequired()])
    port = wtf.IntegerField(
        'Port', validators=[wtfv.InputRequired(), wtfv.NumberRange(
            min=0, max=65535,
            message="Not a valid port (valid range: 0-65535)")])
    user = wtf.StringField('User', validators=[wtfv.InputRequired()])
    password = wtf.PasswordField('Password or Passphrase')
    ssh_key = wtf.FileField('SSH Key')

    def to_dict(self) -> dict:
        data = dict(
            name=self.name.data,
            host=self.host.data,
            port=self.port.data,
            user=self.user.data,
            password=self.password.data,
            ssh_key=self.ssh_key.data
        )
        return data

    def validate_name(form: FlaskForm, field: wtf.StringField):
        """
        Checks that the name given to the HPC system does not already
        exist in the system.

        Parameters
        ----------
        form : flask_wtf.FlaskForm
            Form containing the 'name' field.
        field : wtforms.StringField
            'name' field to validate.

        Returns
        -------
        None

        Raises
        ------
        wtforms.validators.ValidationError -- A HPC system exists with\
                                              that name.
        """
        hpcs = fia_mm.HPCSystem.get_by_name(field.data)
        if hpcs is not None:
            raise wtfv.ValidationError(
                'A HPC system with this name already exists in the system. '
                'Please use a different one.')


class EditSystemSettingsForm(FlaskForm):
    """
    Form to edit the system settings.

    Attributes
    ----------
    submit : wtforms.SubmitField
        Submit button.
    """
    submit = wtf.SubmitField('Save')
    # pagination
    items_pp = wtf.IntegerField('Items per page',
                                validators=[wtfv.InputRequired(),
                                            wtfv.NumberRange(min=1, max=100)])

    def __init__(self, app_config: FlaskConfig, *args, **kwargs):
        """
        Default constructor.

        Attributes
        ----------
        app_config : flask.config.Config
            XXX
        args : List
            List of all arguments passed to the parent constructor
        kwargs : Dictionary
            Dictionary of keyword arguments passed to the parent constructor.
        """
        super(EditSystemSettingsForm, self).__init__(*args, **kwargs)
        self.items_pp.data = app_config['ITEMS_PER_PAGE']

    def to_dict(self) -> dict:
        data = dict(
            items_pp=self.items_pp.data
        )
        return data
