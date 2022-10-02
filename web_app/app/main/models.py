"""
Definition of database models for the main module.
"""

from flask_login import UserMixin as FlaskUserMixin
from datetime import datetime
from werkzeug.security import check_password_hash as ws_check_password_hash

from app.db import db
from app.db import (
    BaseModelMixin as FIABaseModelMixin,
    PaginatedAPIMixin as FIAPaginatedAPIMixin
)


class User(db.Model, FIABaseModelMixin, FIAPaginatedAPIMixin, FlaskUserMixin):
    """
    Someone identified within the FuzzItAll service.

    Attributes:
    -----------
    id : Column
        Internal user identifier.
    username : Column
        Name identifying the user.
    password : Column
        Password to protect the user's identity.
    admin: Column
        Whether the user has administration permissions or not.
    created : Column
        User creation date.
    last_login : Column
        Date of last user login.

    Methods
    -------
    check_password(str): bool
        Checks that the given password matches the stored one.
    get_by_username(str):
        Retrieves a user by its username.
    """

    __tablename__ = 'fia_user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    last_login = db.Column(db.DateTime, nullable=True)

    def __str__(self):
        return f'<User ({self.username}{", Admin" if self.admin else None})>'

    def to_dict(self) -> dict:
        data = dict(
            id=self.id,
            username=self.username,
            password=self.password,
            admin=self.admin,
            created=self.created,
            last_login=self.last_login
        )
        return data

    def check_password(self, password: str) -> bool:
        """
        Checks that the given password matches the stored one.

        Parameters
        ----------
        password : str
            Password to be checked (without encryption).

        Returns
        -------
        check_password_hash : bool
            Whether the password hash matches or not.
        """
        return ws_check_password_hash(self.password, password)

    @staticmethod
    def get_by_username(username: str):
        return User.query.filter_by(username=username).first()


class HPCSystem(db.Model, FIABaseModelMixin, FIAPaginatedAPIMixin):
    """
    Remote HPC system with FuzzItAll installed.

    Attributes
    ----------
    id : Column
        Internal HPC system identifier.
    name : Column
        Name of the remote HPC system.
    host : Column
        Name or IP address of the remote HPC system.
    port : Column
        Port enabled on remote host for SSH connection.
    user : Column
        Username for the SSH connection.
    password : Column
        Password for username.
    max_tasks : Column
        Maximum number of parallel tasks.
    max_wall_time : Column
        Maximum wall clock time.
    TODO (gonestco): add ssh key
    TODO (gonestco): add list of fuzzers available
    """

    __tablename__ = 'fia_hpc_system'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    host = db.Column(db.String(128), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    user = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    max_tasks = db.Column(db.Integer, nullable=False)
    max_wall_time = db.Column(db.Float, nullable=False)

    def __str__(self):
        return f'<HPCSystem ({self.name} | {self.host}:{self.port})>'

    def to_dict(self) -> dict:
        data = dict(
            id=self.id,
            name=self.name,
            host=self.host,
            port=self.port,
            user=self.user,
            max_tasks=self.max_tasks,
            max_wall_time=self.max_wall_time
        )
        return data

    @staticmethod
    def get_by_name(name: str):
        return HPCSystem.query.filter_by(name=name).first()

    @staticmethod
    def get_all_for_select():
        return HPCSystem.query.with_entities(HPCSystem.id,
                                             HPCSystem.name,
                                             HPCSystem.max_tasks,
                                             HPCSystem.max_wall_time).all()
