"""
Definition of forms related to the registration module.
"""

from flask_wtf import FlaskForm
import wtforms as wtf
import wtforms.validators as wtfv


class RegisterForm(FlaskForm):
    """
    Form to register for access the service.

    Attributes
    ----------
    name : wtforms.SubmitField
        Submit button.
    name : wtforms.StringField
        Name of user to contact.
    email : wtforms.EmailField
        User's email to contact.
    agree : wtforms.BooleanField
        Consent to user registration.
    """
    submit = wtf.SubmitField('Sign Up', render_kw={'disabled': 'disabled'})
    # contact data
    name = wtf.StringField('Name', validators=[wtfv.InputRequired()])
    email = wtf.EmailField(
        'E-mail', validators=[wtfv.InputRequired()])
    # agreement
    agree = wtf.BooleanField(
        'Yes, I would like to sign up for access to the service',
        validators=[wtfv.InputRequired()])
