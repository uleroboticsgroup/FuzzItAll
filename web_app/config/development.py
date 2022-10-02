from config.default import *

# --------------------------------------------------------------------
#   ENVIRONMENT DEFINITION
# --------------------------------------------------------------------
APP_ENV = APP_ENV_DEVELOPMENT

# --------------------------------------------------------------------
#   DATABASE CONFIGURATION
# --------------------------------------------------------------------
SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/instance/fuzzitalldb-dev.db'
