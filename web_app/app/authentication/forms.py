"""
Definition of forms related to the authentication module.
"""

from flask_wtf import FlaskForm
import wtforms as wtf
import wtforms.validators as wtfv


class LoginForm(FlaskForm):
    """
    Form to define access credentials to the FuzzItAll web service.

    Attributes
    ----------
    submit : wtforms.SubmitField
        Submit button.
    username : wtforms.StringField
        Name identifying the user in the service.
    password : wtforms.PasswordField
        Password to protect the user's identity.
    remember : wtforms.BooleanField
        Whether or not remember the user's session cookie.
    """
    submit = wtf.SubmitField('Sign In')
    # credentials
    username = wtf.StringField('Username', validators=[wtfv.InputRequired()])
    password = wtf.PasswordField('Password', validators=[wtfv.InputRequired()])
    # session cookie
    remember = wtf.BooleanField('Remember Me')

    def to_dict(self) -> dict:
        data = dict(
            username=self.username.data,
            password=self.password.data,
            remember=self.remember.data
        )
        return data
