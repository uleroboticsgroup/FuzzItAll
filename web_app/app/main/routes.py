"""
Flask blueprint for handling the views of the main module.
"""

import flask as f
import flask_login as fl

# --------------------------------------------------------------------
#   BLUEPRINT DECLARATION
# --------------------------------------------------------------------

main_bp = f.Blueprint('main', __name__, template_folder='templates')

# --------------------------------------------------------------------
#   ROUTES DEFINITION
# --------------------------------------------------------------------


@main_bp.route('/', methods=['GET'])
def index():
    '''
    Either shows landing page for unauthenticated users or the dashboard
    page for authenticated users.

        Returns:
            redirect (flask.Response):
                Object to redirect to the route showing the dashboard.
            render_template (str):
                HTML code to render the landing page.
    '''
    if fl.current_user.is_authenticated:
        return f.redirect(f.url_for('main.dashboard'))
    else:
        return f.render_template('index.html')


@main_bp.route('/help', methods=['GET'])
def help():
    '''
    Shows the help page.

        Returns:
            render_template (str):
                HTML code to render the help page.
    '''
    return f.render_template('help.html')


@main_bp.route('/dashboard', methods=['GET'])
@fl.login_required
def dashboard():
    '''
    Displays dashboard page.

        Returns:
            render_template (str):
                HTML code to render the dashboard page.
    '''
    return f.render_template('dashboard.html')
