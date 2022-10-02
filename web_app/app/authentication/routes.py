"""
Flask blueprint for handling the views of the authentication module.
"""

import logging
import flask as f
import flask_login as fl

import app.authentication.helpers as fia_auh
import app.authentication.forms as fia_auf
from app.authentication.exceptions import AuthenticationError

# --------------------------------------------------------------------
#  LOGGER DECLARATION
# --------------------------------------------------------------------

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
#   BLUEPRINT DECLARATION
# --------------------------------------------------------------------

auth_bp = f.Blueprint('authentication', __name__,
                      template_folder='templates', url_prefix='/auth')

# --------------------------------------------------------------------
#   ROUTES DEFINITION
# --------------------------------------------------------------------


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Logs a user in the FuzzItAll web service.

        Returns:
            render_template (str):
                HTML code to render the form that allows a user to log
                in to the service.
            redirect (flask.Response):
                Object to redirect either to the view showing the dashboard
                or to the view just before the one from which this route
                was reached.
    '''
    # avoid multiple logins from current user
    if fl.current_user.is_authenticated:
        return f.redirect(f.url_for('main.dashboard'))

    # create the form and validate it on submission
    form = fia_auf.LoginForm()
    if form.validate_on_submit():
        credentials = form.to_dict()

        # attempt to login with given credentials
        login_attempt = f'({credentials["username"]}@{f.request.remote_addr})'
        try:
            fia_auh.login_to_service(**credentials)
            logger.info(f'Successful user login {login_attempt}.')

            # compute next page and redirect the user to it
            next_page = f.request.args.get('next')
            if next_page:
                return f.redirect(next_page)
            else:
                return f.redirect(f.url_for('main.dashboard'))
        except AuthenticationError as e:
            logger.error(f'User login failed {login_attempt}. Reason: {e}')
            f.flash(str(e))

    template_context = dict(form=form)

    return f.render_template('login.html', **template_context)


@auth_bp.route('/logout', methods=['GET'])
def logout():
    '''
    Logs a user out of the FuzzItAll web service.

        Returns:
            redirect (flask.Response):
                Object to redirect to the view showing the index page.
    '''
    logout_attempt = f'({fl.current_user.username}@{f.request.remote_addr})'

    fl.logout_user()
    logger.info(f'Successful user logout {logout_attempt}.')

    return f.redirect(f.url_for('main.index'))
