import os
import os.path as osp
import secrets as s

# --------------------------------------------------------------------
#   CORE CONFIGURATION
# --------------------------------------------------------------------
SECRET_KEY = os.environ.get('FIA_SECRET_KEY') or s.token_urlsafe(32)

# --------------------------------------------------------------------
#   DIRECTORIES CONFIGURATION
# --------------------------------------------------------------------
BASE_DIR = osp.dirname(osp.dirname(osp.abspath(__file__)))
TMP_DIR = osp.join(BASE_DIR, 'instance', 'tmp')
LOG_DIR = osp.join(BASE_DIR, 'instance', 'log')
LOG_FILE = osp.join(LOG_DIR, 'fuzzitall.log')

# --------------------------------------------------------------------
#   DATABASE CONFIGURATION
# --------------------------------------------------------------------
SQLALCHEMY_TRACK_MODIFICATIONS = False

# --------------------------------------------------------------------
#   APP ENVIRONMENTS
# --------------------------------------------------------------------
APP_ENV_TESTING = 'testing'
APP_ENV_DEVELOPMENT = 'development'
APP_ENV_PRODUCTION = 'production'
APP_ENV = ''

# --------------------------------------------------------------------
#   PAGING
# --------------------------------------------------------------------
ITEMS_PER_PAGE = 15
