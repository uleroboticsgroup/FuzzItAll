"""
Flask blueprint for handling the views of the fuzzing module.
"""

import logging
import flask as f
import flask_login as fl

import app.main.helpers as fia_mh
from app.main.models import HPCSystem

import app.fuzzing.helpers as fia_fh
from app.fuzzing.models import Project
from app.fuzzing.forms import CreateProjectForm
from app.fuzzing.utils import FuzzItAllClient

# --------------------------------------------------------------------
#  LOGGER DECLARATION
# --------------------------------------------------------------------

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
#   BLUEPRINT DECLARATION
# --------------------------------------------------------------------

fuzz_bp = f.Blueprint('fuzzing', __name__,
                      template_folder='templates', url_prefix='/fuzz')

# --------------------------------------------------------------------
#   ROUTES DEFINITION
# --------------------------------------------------------------------


@fuzz_bp.route('/projects', methods=['GET'])
@fl.login_required
def browse_projects():
    '''
    Shows projects related to current user. If the user is an administrator,
    shows all projects created in the web service.

        Request arguments:
            page (int):
                1-based page number.
            per_page (int):
                Page size. Must be greater than 0 and less or equal than 100.
            col (str):
                Column used to sort the project's list by. Must be one of\
                the project's attributes (see app.fuzzing.models.Project).
            dir (str):
                Direction to sort the results by. Must be 'asc' or 'desc'.

        Returns:
            render_template (str):
                HTML code to render current user's projects.
    '''
    # retrieve http request parameters
    page, per_page, col, dir = fia_mh.get_pagination_params(
        f.request.args, Project.name.name)

    # retrieve all projects (with pagination)
    query = Project.query \
        if fl.current_user.admin else Project.get_by_user(fl.current_user.id)
    query = Project.get_sorted_query(query, col, dir)
    projects = Project.to_collection_dict(
        query, page, per_page, col=col, dir=dir)

    template_context = dict(
        items=projects['items'], page_meta=projects['_meta'])

    return f.render_template('projects/browse.html', **template_context)


@fuzz_bp.route('/projects/create', methods=['GET', 'POST'])
@fl.login_required
def create_project():
    '''
    Creates a new project in the local database and requests its execution
    to a HPC system.

        Returns:
            render_template (str):
                HTML code to render the form to create a new project.
            redirect (flask.Response):
                Object to redirect to the route showing all projects of\
                the current user.
            jsonify (flask.Response):
                List of errors, in JSON format, corresponding to the\
                validation of the form.
    '''
    hpcs_avail = HPCSystem.get_all_for_select()
    form_data = f.request.form if (f.request.method == 'POST') else None

    # create the form and validate it on submission
    form = CreateProjectForm(hpcs_avail, data=form_data)
    if f.request.method == 'POST':
        errors = None
        if form.validate():
            data = form.to_dict()
            data['user_id'] = fl.current_user.id

            try:
                fia_fh.create_project(**data)

                logger.info(f'User "{fl.current_user.username}" successfully '
                            f'created project with name=\"{data["name"]}\".')

                f.flash('Project created successfully.')
                return f.redirect(f.url_for('fuzzing.browse_projects'))
            except Exception as e:
                errors = dict(form=[str(e)])
        else:
            errors = form.errors

        return f.jsonify(errors), 400

    template_context = dict(
        form=form,
        hpcs_data=[dict(hpc) for hpc in hpcs_avail]
    )

    return f.render_template('projects/create.html', **template_context)


@fuzz_bp.route('/projects/<int:project_id>', methods=['GET'])
@fl.login_required
def read_project(project_id: int):
    '''
    Shows the details of a given project.

        Parameters:
            project_id (int):
                Identifier of the project.

        Returns:
            render_template (str):
                HTML code to render the details of the project.
    '''
    project = fia_fh.get_project_owned_by_user(project_id, fl.current_user)
    hpcs = HPCSystem.get_by_id(project.hpcs_id)
    template_context = None
    with FuzzItAllClient(hpcs) as fia_client:
        template_context = dict(
            title=f'{project.name}',
            subtitle=f'Fuzzing project details',
            project=project.to_dict(include_jobs=True),
            # TODO(gonestco): remove this stats...
            stats=fia_client.get_stats(project)
        )

    return f.render_template('projects/read.html', **template_context)


@fuzz_bp.route('/projects/<int:project_id>/download', methods=['GET'])
@fl.login_required
def download_project(project_id: int):
    '''
    Downloads the fuzzing results of a project.

        Parameters:
            project_id (int):
                Identifier of the project.

        Returns:
            send_file (flask.Response):
                Zip file containing the fuzzing results.
    '''
    archive = fia_fh.download_project_results(project_id, fl.current_user.id)
    # TODO (gonestco): create async celery task to remove this archive
    # src: https://stackoverflow.com/questions/24612366/delete-an-uploaded-file-after-downloading-it-from-flask

    return f.send_file(archive, mimetype='application/zip', as_attachment=True)


@fuzz_bp.route('/projects/<int:project_id>/delete', methods=['DELETE'])
@fl.login_required
def delete_project(project_id: int):
    '''
    Deletes a project from the web service.

        Parameters:
            project_id (int):
                Identifier of the project.

        Returns:
            redirect (flask.Response):
                Object to redirect either to the route showing all projects
                of the current user (if the operation was successful)
                or to the route showing the details of the project.
    '''
    try:
        fia_fh.request_project_deletion(project_id, fl.current_user.id)
        msg = f'Project with id={project_id} has been successfully deleted.'
        logger.info(msg)
        f.flash(msg)
        return f.redirect(f.url_for('fuzzing.browse_projects'))
    except Exception as e:
        msg = f'Unable to delete project with id={project_id}. Reason: {e}.'
        logger.error(msg)
        f.flash(msg)
        return f.redirect(
            f.url_for('fuzzing.show_project', project_id=project_id))


@fuzz_bp.route('/projects/<int:project_id>/tasks/refresh', methods=['PUT'])
@fl.login_required
def refresh_project_tasks(project_id: int):
    '''
    Updates the fuzzing tasks associated with a project.

        Parameters:
            project_id (int):
                Identifier of the project.

        Returns:
            redirect (flask.Response):
                Object to redirect to the route showing the details\
                of the project.
    '''
    try:
        fia_fh.refresh_fuzzing_job(project_id, fl.current_user.id)
    except Exception as e:
        msg = f'Unable to refresh project with id={project_id}. Reason: {e}'
        logger.error(msg)
        f.flash(msg)

    return f.redirect(f.url_for('fuzzing.read_project', project_id=project_id))


@fuzz_bp.route('/projects/<int:project_id>/tasks/cancel', methods=['PUT'])
@fl.login_required
def cancel_project_tasks(project_id: int):
    '''
    Cancels the execution of fuzzing tasks associated with a project.

        Parameters:
            project_id (int):
                Identifier of the project.

        Returns:
            redirect (flask.Response):
                Object to redirect to the route showing the details\
                of the project.
    '''
    try:
        fia_fh.cancel_fuzzing_job(project_id, fl.current_user.id)
        fia_fh.refresh_fuzzing_job(project_id, fl.current_user.id)
    except Exception as e:
        msg = f'Unable to cancel tasks from project with id={project_id}. Reason: {e}'
        logger.error(msg)
        f.flash(msg)

    return f.redirect(f.url_for('fuzzing.show_project', project_id=project_id))
