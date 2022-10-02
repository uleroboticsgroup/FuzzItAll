"""
Flask blueprint for handling the views of the demo module.
"""

import flask as f

from app.registration.forms import RegisterForm

# --------------------------------------------------------------------
#   BLUEPRINT DECLARATION
# --------------------------------------------------------------------

reg_bp = f.Blueprint('registration', __name__, template_folder='templates')

# --------------------------------------------------------------------
#   ROUTES DEFINITION
# --------------------------------------------------------------------


@reg_bp.route('/signup', methods=['GET'])
def sign_up():
    '''
    Displays the sign up page.

        Returns:
            render_template (str):
                HTML code to render the sign up page.
    '''
    form = RegisterForm()

    template_context = dict(form=form)

    return f.render_template('signup.html', **template_context)
