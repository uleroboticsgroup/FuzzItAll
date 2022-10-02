"""
Declaration and instantiation of third party Flask modules.
"""

from flask import Flask
from flask_login import LoginManager
import logging


# --------------------------------------------------------------------
#   THIRD PARTY MODULES INSTANTIATION
# --------------------------------------------------------------------

login_manager = LoginManager()
login_manager.login_view = 'authentication.login'
login_manager.login_message_category = 'info'


# --------------------------------------------------------------------
#   THIRD PARTY MODULES INITIALIZATION FUNCTIONS
# --------------------------------------------------------------------

def configure_logging(app: Flask):
    '''
    Configure the logging module.

        Parameters:
            app (Flask):
                FuzzItAll web application.

        Returns:
            None
    '''
    # remove default handlers, if any
    del app.logger.handlers[:]

    # add default logger to the list of loggers
    loggers = [app.logger, ]
    handlers = []

    # setup logging configuration
    verbose_formatter = logging.Formatter(
        '[%(asctime)s.%(msecs)d]\t %(levelname)s '
        '\t[%(name)s.%(funcName)s:%(lineno)d]\t %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S')
    debug_envs = [app.config['APP_ENV_DEVELOPMENT'],
                  app.config['APP_ENV_TESTING']]
    log_level = logging.DEBUG \
        if (app.config['APP_ENV'] in debug_envs) else logging.INFO

    # create a handler to write messages via console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(verbose_formatter)
    handlers.append(console_handler)

    # and another to write messages to a log file
    file_handler = logging.FileHandler(app.config['LOG_FILE'])
    file_handler.setLevel(log_level)
    file_handler.setFormatter(verbose_formatter)
    handlers.append(file_handler)

    # then, associate each handler with each of the loggers
    for logger in loggers:
        for handler in handlers:
            logger.addHandler(handler)
        logger.propagate = False
        logger.setLevel(log_level)
