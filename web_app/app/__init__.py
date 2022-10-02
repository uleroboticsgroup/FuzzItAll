"""
FuzzItAll web application.
"""

from flask import Flask

from app.db import db
import app.ext as ext
from app import (
    main, authentication, administration, fuzzing, registration
)
from app.main.routes import main_bp
from app.administration.routes import admin_bp
from app.authentication.routes import auth_bp
from app.fuzzing.routes import fuzz_bp
from app.registration.routes import reg_bp


def create_app(settings_module):
    '''
    Creates the FuzzItAll web application.

        Parameters:
            settings_module (object | str):
                FuzzItAll settings module to be loaded.

        Returns:
            app (Flask):
                FuzzItAll web application.
    '''
    # create the web application and load its configuration
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(settings_module)

    # initialize database and third party modules
    db.init_app(app)
    ext.login_manager.init_app(app)
    ext.configure_logging(app)

    # initialize custom modules
    main.init_app(app)
    administration.init_app(app)
    authentication.init_app(app)
    fuzzing.init_app(app)
    registration.init_app(app)

    # register all blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(fuzz_bp)
    app.register_blueprint(reg_bp)

    return app
