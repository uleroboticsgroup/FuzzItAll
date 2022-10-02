"""
Flask blueprint for handling the views of the administration module.
"""

import logging
import flask as f
import flask_login as fl

from app.main.models import User, HPCSystem
import app.main.helpers as fia_mh

import app.administration.helpers as fia_adh
import app.administration.forms as fia_adf

# --------------------------------------------------------------------
#  LOGGER DECLARATION
# --------------------------------------------------------------------

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
#   BLUEPRINT DECLARATION
# --------------------------------------------------------------------

admin_bp = f.Blueprint('administration', __name__,
                       template_folder='templates', url_prefix='/admin')

# --------------------------------------------------------------------
#   USER-RELATED ROUTES DEFINITION
# --------------------------------------------------------------------


@admin_bp.route('/users/', methods=['GET'])
@fl.login_required
@fia_adh.admin_required
def browse_users():
    '''
    Shows users registered in the web service.

        Request parameters:
            page (int):
                1-based page number.
            per_page (int):
                Page size. Must be greater than 0 and less or equal than 100.
            col (str):
                Column used to sort the user's list by. Must be one of\
                the user's attributes (see app.main.models.User).
            dir (str):
                Direction to sort the results by. Must be 'asc' or 'desc'.

        Returns:
            render_template (str):
                HTML code to render the list of users registered.
    '''
    # retrieve http request parameters
    page, per_page, col, dir = fia_mh.get_pagination_params(
        f.request.args, User.username.name)

    # retrieve all users (with pagination)
    query = User.get_sorted_query(User.query, col, dir)
    users = User.to_collection_dict(query, page, per_page, col=col, dir=dir)

    template_context = dict(items=users['items'], page_meta=users['_meta'])

    return f.render_template('users/browse.html', **template_context)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@fl.login_required
@fia_adh.admin_required
def create_user():
    '''
    Registers a new user in the system.

        Returns:
            render_template (str):
                HTML code to render the form to create a new user.
            redirect (flask.Response):
                Object to redirect to the route showing all users registered\
                in the system.
    '''
    # create the form and validate it on submission
    form = fia_adf.CreateUserForm()
    if form.validate_on_submit():
        data = form.to_dict()

        try:
            fia_adh.create_user(**data)

            logger.info(f'User "{fl.current_user.username}" successfully '
                        f'created user with name=\"{data["username"]}\".')

            f.flash('User created successfully.')
            return f.redirect(f.url_for('administration.browse_users'))
        except Exception as e:
            logger.warning(f'User "{fl.current_user.username}" could not '
                           f'create user with name=\"{data["username"]}\". '
                           f'Reason: {e}')
            f.flash('Could not create the user. Please try again.')

    template_context = dict(form=form)

    return f.render_template('users/create.html', **template_context)


@admin_bp.route('/users/<int:user_id>/update', methods=['GET', 'POST'])
@fl.login_required
@fia_adh.admin_required
def update_user(user_id: int):
    """
    Updates the data of a user.

        Parameters:
            user_id (int):
                Idenitifier of the user.

        Returns:
            redirect (flask.Response):
                Object to redirect to the route showing all users.
    """
    # create the form and validate it on submission
    form = fia_adf.ChangePasswordForm()
    if form.validate_on_submit():
        data = form.to_dict()

        try:
            fia_adh.update_user(user_id, **data)

            logger.info(f'User "{fl.current_user.username}" successfully '
                        f'changed password for user with id="{user_id}".')

            f.flash('Password changed successfully.')
            return f.redirect(f.url_for('administration.browse_users'))
        except Exception as e:
            logger.warning(f'User "{fl.current_user.username}" could not '
                           f'change password for user with id="{user_id}". '
                           f'Reason: {e}')
            f.flash(f'Could not update user\'s data. Please try again.')

    template_context = dict(form=form)

    return f.render_template('users/update.html', **template_context)


@admin_bp.route('/users/<int:user_id>/delete', methods=['DELETE'])
@fl.login_required
@fia_adh.admin_required
def delete_user(user_id: int):
    '''
    Deletes a user from the system.

        Parameters:
            user_id (int):
                Identifier of the user.

        Returns:
            redirect (flask.Response):
                Object to redirect to the route showing all users.
    '''
    try:
        fia_adh.delete_user(user_id)

        logger.info(f'User "{fl.current_user.username}" successfully '
                    f'deleted user with id="{user_id}".')

        f.flash('User has been successfully deleted.')
    except Exception as e:
        logger.warning(f'User "{fl.current_user.username}" could not '
                       f'delete user with id="{user_id}". '
                       f'Reason: {e}')
        f.flash(f'Could not delete the user. Please try again.')

    return f.redirect(f.url_for('administration.browse_users'))


# --------------------------------------------------------------------
#   HPC SYSTEM-RELATED ROUTES DEFINITION
# --------------------------------------------------------------------


@admin_bp.route('/hpcs/', methods=['GET'])
@fl.login_required
@fia_adh.admin_required
def browse_hpcs():
    '''
    Shows HPC systems configured in the web service.

        Request parameters:
            page (int):
                1-based page number.
            per_page (int):
                Page size. Must be greater than 0 and less or equal than 100.
            col (str):
                Column used to sort the HPC system's list by. Must be one of\
                the HPC system's attributes (see app.main.models.HPCSystem).
            dir (str):
                Direction to sort the results by. Must be 'asc' or 'desc'.

        Returns:
            render_template (str):
                HTML code to render the list of HPC systems.
    '''
    # retrieve http request parameters
    page, per_page, col, dir = fia_mh.get_pagination_params(
        f.request.args, HPCSystem.name.name)

    # retrieve all hpc systems (with pagination)
    query = HPCSystem.get_sorted_query(HPCSystem.query, col, dir)
    hpcs = HPCSystem.to_collection_dict(
        query, page, per_page, col=col, dir=dir)

    template_context = dict(items=hpcs['items'], page_meta=hpcs['_meta'])

    return f.render_template('hpcs/browse.html', **template_context)


@admin_bp.route('/hpcs/create', methods=['GET', 'POST'])
@fl.login_required
@fia_adh.admin_required
def create_hpcs():
    '''
    Configures a new HPC system in the web service.

        Returns:
            render_template (str):
                HTML code to render the form to create a new HPC system.
            redirect (flask.Response):
                Object to redirect to the route showing all HPC systems\
                configured in the system.
    '''
    # create the form and validate it on submission
    form = fia_adf.CreateHPCSystemForm()
    if form.validate_on_submit():
        data = form.to_dict()

        try:
            fia_adh.create_hpcs(**data)

            logger.info(f'User "{fl.current_user.username}" successfully '
                        f'created HPC system with name=\"{data["name"]}\".')

            f.flash('HPC System created successfully.')
            return f.redirect(f.url_for('administration.browse_hpcs'))
        except Exception as e:
            logger.warning(f'User "{fl.current_user.username}" could not '
                           f'create HPC system with '
                           f'name=\"{data["name"]}\". Reason: {e}')
            f.flash('Could not create the HPC system. Please try again.')

    template_context = dict(form=form)

    return f.render_template('hpcs/create.html', **template_context)


@admin_bp.route('/hpcs/<int:hpcs_id>/delete', methods=['DELETE'])
@fl.login_required
@fia_adh.admin_required
def delete_hpcs(hpcs_id: int):
    '''
    Deletes a HPC system from the FuzzItAll web service.

        Parameters:
            hpcs_id (int):
                Identifier of the HPC system.

        Returns:
            redirect (flask.Response):
                Object to redirect to the route showing all HPC systems.
    '''
    try:
        fia_adh.delete_hpcs(hpcs_id)

        logger.info(f'User "{fl.current_user.username}" successfully '
                    f'deleted HPC system with id="{hpcs_id}".')
        f.flash('HPC system has been successfully deleted.')
    except Exception as e:
        logger.warning(f'User "{fl.current_user.username}" could not '
                       f'delete HPC system with id="{hpcs_id}". '
                       f'Reason: {e}')
        f.flash(f'Could not delete the HPC system. Please try again.')

    return f.redirect(f.url_for('administration.browse_hpcs'))


# --------------------------------------------------------------------
#   SYSTEM-RELATED ROUTES DEFINITION
# --------------------------------------------------------------------


@admin_bp.route('/system', methods=['GET', 'POST'])
@fl.login_required
@fia_adh.admin_required
def browse_system():
    """
    Displays both system configuration settings and system log.

        Parameters:
            None

        Returns:
            render_template (str):
                HTML code to render the system settings.
    """
    # read log file
    with open(f.current_app.config['LOG_FILE']) as log_file:
        log = log_file.readlines()

    # create the system settings form
    form = fia_adf.EditSystemSettingsForm(f.current_app.config)
    if form.validate_on_submit():
        data = form.to_dict()

        try:
            fia_adh.save_system_settings(**data)

            logger.info(f'User "{fl.current_user.username}" updated system '
                        f'settings.')

            f.flash('System settings saved.')
        except Exception as e:
            logger.warning(f'User "{fl.current_user.username}" failed to '
                           f'update system settings. Reason: {e}')
            f.flash('Could not save system settings. Please try again.')

    template_context = dict(log=log, form=form)

    return f.render_template('system/browse.html', **template_context)


@admin_bp.route('/system/log', methods=['GET'])
@fl.login_required
@fia_adh.admin_required
def download_system_log():
    """
    Downloads current system log.

        Parameters:
            None

        Returns:
            send_file (flask.Response):
                System log file.
    """
    return f.send_file(f.current_app.config['LOG_FILE'],
                       mimetype='text/plain', as_attachment=True)
