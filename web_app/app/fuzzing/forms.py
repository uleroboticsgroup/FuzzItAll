"""
Definition of forms related to the fuzzing module.
"""

from flask_wtf import FlaskForm
import wtforms as wtf
import wtforms.validators as wtfv
import datetime as dt

import app.fuzzing.models as fia_fm
from app.fuzzing.helpers import ping_repository


class CreateProjectForm(FlaskForm):
    """
    Form to define the creation of a project.

    Attributes
    ----------
    submit : SubmitField
        Submit button.
    name : StringField
        Name of the project.
    url : URLField
        URL of the repository containing the source code of the project.
    need_token : RadioField
        Option to determine whether the repository needs credentials.
    tokens : SelectField
        Token that allows access to the given repository (optional).
    hpcs : SelectField
        HPC system in which the project will be run.
    num_tasks : IntegerRangeField
        Number of parallel tasks that will run the fuzzing process.

    Methods
    -------
    validate_name(name):
        Checks that the name given to the project does not already
        exist in the database.
    validate_url(url):
        Checks that the given repository URL is valid, i.e. it exists
        and corresponds to a Git repository.
    validate_need_token(option):
        Checks that, when a token is selected, there are options
        available.
    validate_hpcs(option):
        Checks if the selected HPC is valid.
    """
    submit = wtf.SubmitField('Submit')
    # project details
    name = wtf.StringField('Name', validators=[wtfv.InputRequired()])
    url = wtf.URLField('Repository URL',
                       validators=[wtfv.InputRequired(), wtfv.url()])
    need_token = wtf.RadioField('Does this repository need credentials?',
                                choices=[('n', 'No'), ('y', 'Yes')],
                                default='n')
    tokens = wtf.SelectField(coerce=int, validators=[wtfv.Optional()])
    # hpc settings
    hpcs = wtf.SelectField('HPC System', coerce=int)
    wall_time_dd = wtf.IntegerField('Wall time limit (Days)', default=0)
    wall_time_hhmm = wtf.DateTimeField('Wall time limit (Hours:Minutes)',
                                       format="%H:%M",
                                       default=dt.datetime.strptime("00:00", "%H:%M"))
    # fuzzing settings
    num_tasks = wtf.IntegerRangeField('Number of parallel tasks', default=0)

    def __init__(self, hpcs_avail: list, tokens_avail: list = [],
                 *args, **kwargs):
        """
        Default constructor.

        Attributes
        ----------
        hpcs_avail : list
            List of HPC systems available for submitting the project.
        tokens_avail : list
            List of tokens available for current user.
        args : List
            List of all arguments passed to the parent constructor
        kwargs : Dictionary
            Dictionary of keyword arguments passed to the parent constructor.
        """
        super(CreateProjectForm, self).__init__(*args, **kwargs)
        # initialize the select fields with the given data
        self.tokens.choices = [
            (token.id, token.name) for token in tokens_avail
        ]
        self.hpcs.choices = [(0, "Please select an option...")] + \
            [(hpcs.id, hpcs.name) for hpcs in hpcs_avail]

    def validate_name(self, name: str):
        """
        Checks that the name given to the project does not already exist
        in the database.

        Parameters
        ----------
        name : str
            HTML code of the 'name' attribute.

        Returns
        -------
        None

        Raises
        ------
        ValidationError -- A project exists with that name.
        """
        project = fia_fm.Project.get_by_name(name.data)
        if project is not None:
            raise wtfv.ValidationError(
                f'A project already exists with that name. '
                f'Please use a different one.')

    def validate_url(self, url: str):
        """
        Checks that the given repository URL is valid, i.e. it exists
        and corresponds to a Git repository.

        Parameters
        ----------
        url : str
            HTML code of the 'url' attribute.

        Returns
        -------
        None

        Raises
        ------
        ValidationError -- Given URL does not exist or is not a valid
                            Git repository.
        """
        if not url.data.endswith('.git'):
            raise wtfv.ValidationError(
                f'The given URL is not a valid Git repository.')
        token_id = self.tokens.data if self.need_token.data == 'y' else None
        if not ping_repository(url.data, token_id):
            raise wtfv.ValidationError(
                f'The given URL does not exist or has an error. '
                f'Please check it and try again.')

    def validate_need_token(self, option: str):
        """
        Checks that, when a token is selected, there are options available.

        Parameters
        ----------
        option : str
            HTML code of the 'need_token' attribute.

        Returns
        -------
        None

        Raises
        ------
        ValidationError -- Token was selected but there were no options.
        """
        if option.data == 'y' and len(self.tokens.choices) == 0:
            raise wtfv.ValidationError('No access token selected.')

    def validate_hpcs(self, option: str):
        """
        Checks if the selected HPC is valid.

        Parameters
        ----------
        option : int
            HTML code of the 'hpcs' attribute.

        Returns
        -------
        None

        Raises
        ------
                ValidationError -- No option selected.
        """
        if option.data == 0:
            raise wtfv.ValidationError('Not a valid HPC system selected.')

    def to_dict(self) -> dict:
        data = dict(
            name=self.name.data,
            url=self.url.data,
            token_id=self.tokens.data if self.need_token.data == 'y' else None,
            hpcs_id=self.hpcs.data,
            num_tasks=self.num_tasks.data,
            wall_time=dt.timedelta(days=self.wall_time_dd.data,
                                   hours=self.wall_time_hhmm.data.hour,
                                   minutes=self.wall_time_hhmm.data.minute)
        )
        return data
