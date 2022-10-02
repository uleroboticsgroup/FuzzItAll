"""
Definition of database models for the fuzzing module.
"""

import enum
from datetime import timedelta

from app.db import db
from app.db import (
    BaseModelMixin as FIABaseModelMixin,
    PaginatedAPIMixin as FIAPaginatedAPIMixin
)


class ProjectState(enum.Enum):
    """
    State a project can go through.
    """
    REQUESTED = enum.auto()
    RUNNING = enum.auto()
    FAILED = enum.auto()
    COMPLETED = enum.auto()


class SlurmJobState(enum.Enum):
    """
    State a Slurm job can go through. See the following link for more
    information:

        https://slurm.schedmd.com/squeue.html#SECTION_JOB-STATE-CODES

    """
    BOOT_FAILED = enum.auto()
    CANCELLED = enum.auto()
    COMPLETED = enum.auto()
    CONFIGURING = enum.auto()
    COMPLETING = enum.auto()
    DEADLINE = enum.auto()
    FAILED = enum.auto()
    NODE_FAIL = enum.auto()
    OUT_OF_MEMORY = enum.auto()
    PENDING = enum.auto()
    PREEMPTED = enum.auto()
    RUNNING = enum.auto()
    RESV_DEL_HOLD = enum.auto()
    REQUEUE_FED = enum.auto()
    REQUEUE_HOLD = enum.auto()
    RESIZING = enum.auto()
    REVOKED = enum.auto()
    SIGNALING = enum.auto()
    SPECIAL_EXIT = enum.auto()
    STAGE_OUT = enum.auto()
    STOPPED = enum.auto()
    SUSPENDED = enum.auto()
    TIMEOUT = enum.auto()


class Project(db.Model, FIABaseModelMixin, FIAPaginatedAPIMixin):
    """
    Project containing one or more fuzzing targets.

    Attributes
    ----------
    id : Column
        Internal project identifier.
    user_id : Column
        Identifier of the user owning the project.
    created : Column
        Date of project creation.
    last_update : Column
        Date on which project status was last updated.
    name : Column
        Alias of the project.
    url : Column
        URL of the repository containing the source code.
    hpcs_id : Column
        Identifier of the HPC system this project was submitted to.
    state : Column
        TODO (gonestco): description
    job : relationship
        Slurm job running the fuzzing tasks.

    Methods
    -------
    to_dict(include_job):
        Returns the attributes as a dictionary.
    get_by_name(name):
        Retrieves a project by its name.
    get_by_user(user_id):
        Retrieves all projects owned by some specific user.
    """

    __tablename__ = 'fia_project'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('fia_user.id'), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    hpcs_id = db.Column(
        db.Integer, db.ForeignKey('fia_hpc_system.id'), nullable=False)
    state = db.Column(
        db.Enum(ProjectState), nullable=False, default=ProjectState.REQUESTED)

    jobs = db.relationship('FuzzingJob', backref='project', lazy='select')

    def __str__(self):
        return f'<Project ({self.name})>'

    def to_dict(self, include_jobs=True) -> dict:
        data = dict(
            id=self.id,
            created=self.created,
            last_update=self.last_update,
            name=self.name,
            url=self.url,
            hpcs_id=self.hpcs_id,
            state=self.state
        )
        if include_jobs:
            data['jobs'] = self.jobs[0].to_dict()

        return data

    def update_project_state(self) -> ProjectState:
        """
        TODO (gonestco): description
        """
        project2job_state = dict(
            REQUESTED=[SlurmJobState.CONFIGURING, SlurmJobState.PENDING,
                       SlurmJobState.RESV_DEL_HOLD, SlurmJobState.REQUEUE_FED,
                       SlurmJobState.REQUEUE_HOLD, SlurmJobState.RESIZING,
                       SlurmJobState.REVOKED],
            RUNNING=[SlurmJobState.COMPLETING, SlurmJobState.RUNNING,
                     SlurmJobState.SIGNALING, SlurmJobState.STAGE_OUT],
            FAILED=[SlurmJobState.BOOT_FAILED, SlurmJobState.CANCELLED,
                    SlurmJobState.DEADLINE, SlurmJobState.NODE_FAIL,
                    SlurmJobState.OUT_OF_MEMORY, SlurmJobState.PREEMPTED,
                    SlurmJobState.STOPPED, SlurmJobState.SUSPENDED],
            COMPLETED=[SlurmJobState.COMPLETED, SlurmJobState.SPECIAL_EXIT,
                       SlurmJobState.TIMEOUT]
        )
        curr_proj_state = [key for key, values in project2job_state.items()
                           if self.jobs[0].state in values].pop(0)
        self.state = ProjectState[curr_proj_state]

    @staticmethod
    def get_by_name(name: str):
        return Project.query.filter_by(name=name).first()

    @staticmethod
    def get_by_user(user_id: int):
        return Project.query.filter_by(user_id=user_id)


class FuzzingJob(db.Model, FIABaseModelMixin):
    """
    Slurm job that performs the fuzzing tasks within an HPC system.

    Attributes
    ----------
    id : Column
        Internal fuzzing job identifier.
    project_id : Column
        Identifier of the project this job is related to.
    job_id : Column
        Identifier of the Slurm job given by the HPC.
    num_tasks : Column
        Number of parallel tasks running the fuzzing process.
    state : Column
        State of the Slurm Job in the HPC system.
    wall_time : Column
        Maximum time (in seconds) the job will be allowed to run in the
        HPC system.
    elapsed_time : Column
        Runtime of the job (in seconds).
    """

    __tablename__ = 'fia_fuzzing_job'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('fia_project.id'))
    job_id = db.Column(db.Integer, nullable=False)
    num_tasks = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Enum(SlurmJobState), nullable=False,
                      default=SlurmJobState.PENDING)
    wall_time = db.Column(db.Float, nullable=False)
    elapsed_time = db.Column(db.Float, nullable=False, default=0.0)

    def __str__(self):
        return f'<FuzzingJob: ({self.job_id}, {self.state})>'

    def to_dict(self) -> dict:
        data = dict(
            id=self.id,
            job_id=self.job_id,
            num_tasks=self.num_tasks,
            state=self.state,
            wall_time=timedelta(seconds=self.wall_time),
            elapsed_time=timedelta(seconds=self.elapsed_time)
        )
        return data
